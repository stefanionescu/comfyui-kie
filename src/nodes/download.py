"""Task: Download, which collects a recorded task that kept running after a cancel, a restart, or a timeout."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, override
import asyncio
from functools import partial

from comfy_api.latest import io

from .outputs import build_node_outputs
from ..state.errors import KIEError, ErrorCode
from ..comfy.runtime import TASKS
from ..comfy.execution import send_request, wait_for_request
from ..config.patterns import TASK_ID_PATTERN
from ..config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES
from ..kie.tasks.operation import collect_task
from ..config.messages.tasks import TASK_UNKNOWN

if TYPE_CHECKING:
    from ..state.files import FileKind

_TASK_ID = re.compile(TASK_ID_PATTERN)
# Every output of every job node; Task: Download fills whichever the task made.
_OUTPUTS = (
    io.Image.Output('images', display_name='images', is_output_list=True),
    io.Mask.Output('masks', display_name='masks', is_output_list=True),
    io.Video.Output('video', display_name='video', is_output_list=True),
    io.Audio.Output('audio', display_name='audio', is_output_list=True),
    io.Custom(SOCKET_TYPES['FILES']).Output('files', display_name='files'),
    io.String.Output('result', display_name='result'),
)
# The node decodes every kind of file a task can make.
_KINDS: frozenset[FileKind] = frozenset({'image', 'video', 'audio'})


async def _download_task(task_id: str, node_id: str | None) -> io.NodeOutput:
    """Read the task's record, wait for the task, and download every file any output can show."""
    record = await asyncio.to_thread(TASKS.read, task_id)
    output_ids = tuple(output.id for output in _OUTPUTS if output.id is not None)
    run = partial(collect_task, record, TASKS, _KINDS)
    return await send_request(run, partial(build_node_outputs, output_ids=output_ids), node_id)


class TaskDownload(io.ComfyNode):
    """Collect one recorded task of any kind, and return everything it made; collecting bills nothing.

    The same task always gives the same outputs, so ComfyUI's cache holds, and this is not a paid node.
    """

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """List the recorded tasks when ComfyUI builds the node definitions; the R key reads them again."""
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='Task: Download',
            category=MENUS['SHARED'],
            description='Collect a KIE task that kept running after a cancel, a restart, or a timeout. '
            'It bills nothing.',
            inputs=[
                io.Combo.Input(
                    'task',
                    options=TASKS.list_labels(),
                    tooltip='A task recorded on this server. Press R to list tasks recorded later.',
                )
            ],
            outputs=list(_OUTPUTS),
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    def validate_inputs(cls, **inputs: object) -> bool | str:
        """Take a task recorded after ComfyUI built the node definitions, as long as the label starts with its ID.

        ComfyUI skips its own list check only for the inputs this method takes as extra keywords.
        """
        return True if _TASK_ID.match(str(inputs.get('task', '')).split(' ', 1)[0]) else TASK_UNKNOWN

    @classmethod
    @override
    async def execute(cls, *, task: str = '') -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] # reason: ComfyUI calls execute with the inputs the schema declares.
        """Collect the chosen task in an owned task, so ComfyUI's cancel stops the wait and keeps the record."""
        task_id = task.split(' ', 1)[0]
        if _TASK_ID.match(task_id) is None:
            raise KIEError(ErrorCode.INVALID_INPUT, TASK_UNKNOWN)
        return await wait_for_request(asyncio.create_task(_download_task(task_id, cls.hidden.unique_id)))


__all__ = ['TaskDownload']
