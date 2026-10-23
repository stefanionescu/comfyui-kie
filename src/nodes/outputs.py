"""Fill the outputs of a job node from what its task made."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from comfy_api.latest import io
from comfy_execution.graph import ExecutionBlocker

from ..comfy.media import decode_audio, decode_video, decode_images

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ..state.tasks import TaskResult


def build_node_outputs(result: TaskResult, output_ids: Sequence[str]) -> io.NodeOutput:
    """Return one value per output ID, in the order given, decoding only the files those outputs show.

    An empty list, and no files, block the nodes connected to them; result always holds the task's result.
    """
    contents = {
        kind: [output.content for output in result.files if output.file.kind == kind and output.content is not None]
        for kind in ('image', 'video', 'audio')
    }
    values: dict[str, object] = {
        'files': tuple(output.file for output in result.files),
        'result': json.dumps(result.result, indent=2, ensure_ascii=False),
    }
    if {'images', 'masks'} & set(output_ids):
        images, masks = decode_images(contents['image'])
        values.update(images=list(images), masks=list(masks))
    if 'video' in output_ids:
        values['video'] = [decode_video(content) for content in contents['video']]
    if 'audio' in output_ids:
        values['audio'] = [decode_audio(content) for content in contents['audio']]
    return io.NodeOutput(*(values.get(output_id) or ExecutionBlocker(None) for output_id in output_ids))


__all__ = ['build_node_outputs']
