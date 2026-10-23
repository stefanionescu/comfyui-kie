"""The three job nodes: Image: Generate, Video: Generate, and Audio: Generate."""

from __future__ import annotations

from typing import ClassVar

from comfy_api.latest import io

from .job import JobNode
from ..config.namespace import SOCKET_TYPES

# The files and the result that every job node returns after its media.
_FILES = io.Custom(SOCKET_TYPES['FILES']).Output('files', display_name='files')
_RESULT = io.String.Output('result', display_name='result')


class ImageGenerate(JobNode):
    """Make or edit images with any KIE image model."""

    kind = 'image'
    description = 'Make or edit images with any KIE image model, named by its model ID.'
    outputs: ClassVar[tuple[io.Output, ...]] = (
        io.Image.Output('images', display_name='images', is_output_list=True),
        io.Mask.Output('masks', display_name='masks', is_output_list=True),
        _FILES,
        _RESULT,
    )


class VideoGenerate(JobNode):
    """Make, edit, extend, lip-sync, or upscale a video with any KIE video model."""

    kind = 'video'
    description = 'Make, edit, extend, lip-sync, or upscale a video with any KIE video model, named by its model ID.'
    outputs: ClassVar[tuple[io.Output, ...]] = (
        io.Video.Output('video', display_name='video', is_output_list=True),
        _FILES,
        _RESULT,
    )


class AudioGenerate(JobNode):
    """Make speech, music, or sound effects with any KIE audio model."""

    kind = 'audio'
    description = 'Make speech, music, or sound effects with any KIE audio model, named by its model ID.'
    outputs: ClassVar[tuple[io.Output, ...]] = (
        io.Audio.Output('audio', display_name='audio', is_output_list=True),
        _FILES,
        _RESULT,
    )


__all__ = ['AudioGenerate', 'ImageGenerate', 'VideoGenerate']
