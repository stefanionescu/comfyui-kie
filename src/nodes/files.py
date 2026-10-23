"""Put links and ComfyUI media into a chain of files, each for a named input of a KIE model."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, cast, override
from dataclasses import replace
from urllib.parse import urlsplit

import torch
from comfy_api.latest import Input, io

from ..state.files import KIEFile
from ..config.media import LINK_SCHEME, MASK_TENSOR, IMAGE_TENSOR, MAX_LINK_CHARACTERS
from ..state.errors import KIEError, ErrorCode
from ..config.patterns import FIELD_NAME_PATTERN
from ..config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES
from ..config.messages.inputs import (
    FILE_LINK,
    FILE_EMPTY,
    SINGLE_VALUE,
    FILE_FIELD_NAME,
    FILE_FIELD_EMPTY,
    FILE_LINK_LENGTH,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

_FIELD_NAME = re.compile(FIELD_NAME_PATTERN)


def _read_field(values: Sequence[str]) -> str:
    """Read the one input name that the files of the node go to, and refuse a name that no model input can have."""
    names = {value.strip() for value in values}
    if len(names) > 1:
        raise KIEError(ErrorCode.INVALID_INPUT, SINGLE_VALUE.format(name='field'))
    field = next(iter(names), '')
    if not field:
        raise KIEError(ErrorCode.INVALID_INPUT, FILE_FIELD_EMPTY)
    if _FIELD_NAME.match(field) is None:
        raise KIEError(ErrorCode.INVALID_INPUT, FILE_FIELD_NAME)
    return field


def _read_link(text: str, field: str) -> tuple[KIEFile, ...]:
    """Read a typed link; blank text adds nothing, and only an https address with a host passes."""
    link = text.strip()
    if not link:
        return ()
    if len(link) > MAX_LINK_CHARACTERS:
        raise KIEError(ErrorCode.INVALID_INPUT, FILE_LINK_LENGTH.format(maximum=MAX_LINK_CHARACTERS))
    parts = urlsplit(link)
    if parts.scheme != LINK_SCHEME or not parts.netloc:
        raise KIEError(ErrorCode.INVALID_INPUT, FILE_LINK)
    return (KIEFile(kind='other', url=link, media=None, origin='link', field=field),)


def _read_media(value: object, field: str) -> tuple[KIEFile, ...]:
    """Split connected media into one local file for each image or mask frame, each audio clip, or the one video."""
    if isinstance(value, torch.Tensor):
        kind = 'image' if value.ndim == IMAGE_TENSOR['DIMENSIONS'] else 'mask'
        frames = value.unsqueeze(0) if value.ndim == MASK_TENSOR['FRAME_DIMENSIONS'] else value
        return tuple(KIEFile(kind=kind, url=None, media=frame, origin='local', field=field) for frame in frames)
    if isinstance(value, dict) and 'waveform' in value and 'sample_rate' in value:
        audio = cast('Input.Audio', cast('object', value))
        waveform = audio['waveform']
        clips = [
            {'waveform': waveform[index : index + 1], 'sample_rate': audio['sample_rate']}
            for index in range(len(waveform))
        ]
        return tuple(KIEFile(kind='audio', url=None, media=clip, origin='local', field=field) for clip in clips)
    if isinstance(value, Input.Video):
        return (KIEFile(kind='video', url=None, media=value, origin='local', field=field),)
    raise KIEError(ErrorCode.INVALID_INPUT, FILE_EMPTY)


def _read_file(value: object, field: str) -> tuple[KIEFile, ...]:
    """Turn one connected or typed value into files for the input: a link, the files of a KIE node, or local media."""
    if isinstance(value, str):
        return _read_link(value, field)
    if isinstance(value, tuple):
        items = cast('tuple[object, ...]', value)
        return tuple(replace(item, field=field) for item in items if isinstance(item, KIEFile))
    return _read_media(value, field)


class FileAdd(io.ComfyNode):
    """Add files for one named input after the files it receives; it uploads nothing and needs no key."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """List the earlier files, the input name, and the file: a typed link, or connected media or files."""
        file = io.String.Input(
            'file',
            default='',
            tooltip='The file to add: a public https:// link typed here, or a connected image, mask, audio, video, or '
            'the files of a KIE node.',
        )
        files_socket = io.Custom(SOCKET_TYPES['FILES'])
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='File: Add',
            category=MENUS['SHARED'],
            description='Add a link, images, masks, audio, a video, or the files of another node for one input of a '
            'KIE model, named in field. A paid node uploads the files when it runs.',
            inputs=[
                files_socket.Input(
                    'files',
                    optional=True,
                    tooltip='Files from another File: Add. The new files go after them, and each keeps its own input.',
                ),
                io.String.Input(
                    'field',
                    default='',
                    tooltip="The model's input, exactly as KIE names it, such as image_urls or reference_audio_urls. "
                    'Model: Info lists the inputs of a model.',
                ),
                io.MultiType.Input(file, types=[io.Image, io.Mask, io.Audio, io.Video, files_socket]),
            ],
            outputs=[files_socket.Output('files', display_name='files')],
            is_input_list=True,
        )

    @classmethod
    @override
    def execute(  # pyright: ignore[reportIncompatibleMethodOverride] # reason: ComfyUI calls execute with the inputs the schema declares.
        cls, *, field: list[str], file: list[object], files: list[tuple[KIEFile, ...]] | None = None
    ) -> io.NodeOutput:
        """Put the new files after the ones received, each with the input name of this node, in the order of the chain.

        With input lists every input arrives as a list, so an image list from a KIE node arrives whole.
        """
        name = _read_field(field)
        earlier = tuple(item for chain in files or () for item in chain)
        added = tuple(item for value in file for item in _read_file(value, name))
        if not added:
            raise KIEError(ErrorCode.INVALID_INPUT, FILE_EMPTY)
        return io.NodeOutput((*earlier, *added))


__all__ = ['FileAdd']
