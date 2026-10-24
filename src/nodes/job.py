"""The paid node that every job node is: any KIE model of its kind, named by its model ID, and one task."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, cast, override
from functools import partial

from comfy_api.latest import io

from .base import PaidNode
from .outputs import build_node_outputs
from ..comfy.media import encode_local_file
from ..state.tasks import TaskRequest
from ..comfy.runtime import TASKS
from ..config.inputs import LINES, TEXTS, CHOICE, SETTINGS, TOOLTIPS, RUN_NUMBER, INPUT_NAMES, NUMBER_RANGES
from ..config.models import KIND_NODES, DEFAULT_MODELS
from ..kie.arguments import parse_input
from ..comfy.execution import send_request
from ..config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES
from ..kie.tasks.operation import run_task

if TYPE_CHECKING:
    from ..state import Json
    from ..state.files import KIEFile
    from ..state.models import Kind, KIEModel


def _build_setting(name: str, start: str | int) -> io.Input:
    """Build one named setting: default sends nothing, and custom shows its value."""
    if isinstance(start, int):
        low, high = NUMBER_RANGES[name]
        value: io.Input = io.Int.Input(CHOICE['VALUE'], default=start, min=low, max=high, tooltip=TOOLTIPS[name])
    else:
        value = io.String.Input(CHOICE['VALUE'], default=start, tooltip=TOOLTIPS[name])
    options = [io.DynamicCombo.Option(CHOICE['DEFAULT'], []), io.DynamicCombo.Option(CHOICE['CUSTOM'], [value])]
    return io.DynamicCombo.Input(name, options=options, tooltip=TOOLTIPS[name])


def _read_settings(kind: Kind, values: dict[str, object]) -> dict[str, Json]:
    """Read the named settings set to custom; default, or no value from a caller that leaves it out, sends nothing."""
    settings: dict[str, Json] = {}
    for name in SETTINGS[kind]:
        choice = values.get(name)
        if not isinstance(choice, dict):
            continue
        selected = cast('dict[str, Json]', choice)
        if selected.get(name) == CHOICE['CUSTOM']:
            settings[name] = selected.get(CHOICE['VALUE'])
    return settings


class JobNode(PaidNode):
    """Run one task on any KIE model of the kind of the node, and fill the outputs of the node.

    Attributes:
        description: The description ComfyUI shows for the node.
        outputs: The output sockets of the node in order; build_node_outputs fills them by ID.

    """

    description: ClassVar[str]
    outputs: ClassVar[tuple[io.Output, ...]]

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """Describe a job node: files, the model, its named settings, the run number, then the text boxes."""
        lines = [
            io.String.Input(name, default=start, tooltip=TOOLTIPS[name]) for name, start in LINES[cls.kind].items()
        ]
        texts = [io.String.Input(name, default='', multiline=True, tooltip=TOOLTIPS[name]) for name in TEXTS[cls.kind]]
        inputs: list[io.Input] = [
            io.Custom(SOCKET_TYPES['FILES']).Input(INPUT_NAMES['FILES'], optional=True, tooltip=TOOLTIPS['FILES']),
            io.String.Input(INPUT_NAMES['MODEL'], default=DEFAULT_MODELS[cls.kind], tooltip=TOOLTIPS['MODEL']),
            *(_build_setting(name, start) for name, start in SETTINGS[cls.kind].items()),
            io.Int.Input(
                INPUT_NAMES['RUN_NUMBER'],
                default=RUN_NUMBER['DEFAULT'],
                min=RUN_NUMBER['MIN'],
                max=RUN_NUMBER['MAX'],
                tooltip=TOOLTIPS['RUN_NUMBER'],
            ),
            *lines,
            *texts,
            io.String.Input(INPUT_NAMES['ARGUMENTS'], default='', multiline=True, tooltip=TOOLTIPS['ARGUMENTS']),
        ]
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name=KIND_NODES[cls.kind],
            category=MENUS[cls.kind.upper()],
            description=cls.description,
            inputs=inputs,
            outputs=list(cls.outputs),
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    def check(cls, model: KIEModel, inputs: dict[str, object]) -> None:
        """Check the text boxes, the named settings, and the arguments that the workflow sets, against the model."""
        names = (*LINES[cls.kind], *TEXTS[cls.kind])
        texts = {name: value if isinstance(value := inputs.get(name), str) else None for name in names}
        arguments = inputs.get(INPUT_NAMES['ARGUMENTS'])
        parse_input(model, texts, _read_settings(cls.kind, inputs), arguments if isinstance(arguments, str) else None)

    @classmethod
    @override
    async def send(cls, node_id: str | None, **inputs: object) -> io.NodeOutput:
        """Send one task and fill the outputs; the task makes every check again, because a link skips them."""
        output_ids = tuple(output.id for output in cls.outputs if output.id is not None)
        files = cast('tuple[KIEFile, ...] | None', inputs.get(INPUT_NAMES['FILES']))
        request = TaskRequest(
            model_id=str(inputs.get(INPUT_NAMES['MODEL'], DEFAULT_MODELS[cls.kind])).strip(),
            texts={name: str(inputs.get(name) or '') for name in (*LINES[cls.kind], *TEXTS[cls.kind])},
            settings=_read_settings(cls.kind, inputs),
            arguments=str(inputs.get(INPUT_NAMES['ARGUMENTS']) or ''),
            files=files or (),
            kind=cls.kind,
        )
        run = partial(run_task, request, encode_local_file, TASKS)
        return await send_request(run, partial(build_node_outputs, output_ids=output_ids), node_id)


__all__ = ['JobNode']
