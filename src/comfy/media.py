"""Check ComfyUI media and convert it with ComfyUI's own helpers: to files for KIE, and back from the files it makes.

Encoding and decoding block, so callers run these functions through wait_for_thread.
"""

from __future__ import annotations

import io
from typing import TYPE_CHECKING, cast
import hashlib

import torch
from comfy_api.latest import Types, InputImpl
from comfy_api_nodes.util.conversions import (
    tensor_to_pil,
    tensor_to_bytesio,
    bytesio_to_image_tensor,
    audio_ndarray_to_bytesio,
    audio_bytes_to_audio_input,  # pyright: ignore[reportUnknownVariableType] # reason: ComfyUI types its result as a bare dict.
    audio_tensor_to_contiguous_ndarray,
)

from ..state.files import EncodedFile
from ..config.media import WAV, WEBP, MASK_TENSOR, IMAGE_TENSOR, ENCODED_FORMATS, DIGEST_CHARACTERS
from ..state.errors import KIEError, ErrorCode
from ..config.messages.media import (
    MASK_SHAPE,
    AUDIO_EMPTY,
    IMAGE_PIXELS,
    IMAGE_CHANNELS,
    AUDIO_UNREADABLE,
    AUDIO_UNWRITABLE,
    IMAGE_UNREADABLE,
    VIDEO_UNREADABLE,
    VIDEO_UNWRITABLE,
)

if TYPE_CHECKING:
    from typing import Literal
    from collections.abc import Sequence

    from comfy_api.latest import Input

    from ..state.files import KIEFile


def _build_encoded(content: bytes, kind: Literal['image', 'mask', 'audio', 'video']) -> EncodedFile:
    """Name an encoded file by its kind and the start of its digest, with the content type of its kind."""
    digest = hashlib.sha256(content).hexdigest()
    encoded = ENCODED_FORMATS[kind]
    file_name = f'{kind}-{digest[:DIGEST_CHARACTERS]}.{encoded["EXTENSION"]}'
    return EncodedFile(content, encoded['CONTENT_TYPE'], file_name, digest)


def _encode_image(frame: torch.Tensor) -> EncodedFile:
    """Encode one image frame as lossless WebP at its own pixels, and refuse one that KIE cannot read."""
    if frame.ndim != IMAGE_TENSOR['DIMENSIONS'] - 1 or frame.shape[-1] not in {
        IMAGE_TENSOR['RGB_CHANNELS'],
        IMAGE_TENSOR['RGBA_CHANNELS'],
    }:
        raise KIEError(ErrorCode.INVALID_INPUT, IMAGE_CHANNELS)
    if not bool(torch.isfinite(frame).all()):
        raise KIEError(ErrorCode.INVALID_INPUT, IMAGE_PIXELS)
    buffer = io.BytesIO()
    try:
        tensor_to_pil(frame.clamp(0, 1), total_pixels=None).save(
            buffer, format='WEBP', lossless=True, exact=True, method=WEBP['METHOD'], quality=WEBP['QUALITY']
        )
    except Exception:  # noqa: BLE001 # reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise KIEError(ErrorCode.MEDIA, IMAGE_CHANNELS) from None
    return _build_encoded(buffer.getvalue(), 'image')


def _encode_mask(frame: torch.Tensor) -> EncodedFile:
    """Encode one mask frame as a one-channel PNG, where a mask value of 1 is white."""
    if frame.ndim != MASK_TENSOR['FRAME_DIMENSIONS']:
        raise KIEError(ErrorCode.INVALID_INPUT, MASK_SHAPE)
    if not bool(torch.isfinite(frame).all()):
        raise KIEError(ErrorCode.INVALID_INPUT, IMAGE_PIXELS)
    try:
        content = tensor_to_bytesio(frame.clamp(0, 1), total_pixels=None, mime_type='image/png').getvalue()
    except Exception:  # noqa: BLE001 # reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise KIEError(ErrorCode.MEDIA, MASK_SHAPE) from None
    return _build_encoded(content, 'mask')


def _encode_audio(audio: Input.Audio) -> EncodedFile:
    """Encode one audio clip as a 16-bit WAV, which keeps every sample."""
    waveform = audio['waveform']
    if waveform.shape[-1] == 0:
        raise KIEError(ErrorCode.INVALID_INPUT, AUDIO_EMPTY)
    try:
        content = audio_ndarray_to_bytesio(
            audio_tensor_to_contiguous_ndarray(waveform),
            audio['sample_rate'],
            container_format=WAV['FORMAT'],
            codec_name=WAV['CODEC'],
        ).getvalue()
    except Exception:  # noqa: BLE001 # reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise KIEError(ErrorCode.MEDIA, AUDIO_UNWRITABLE) from None
    return _build_encoded(content, 'audio')


def _encode_video(video: Input.Video) -> EncodedFile:
    """Write a ComfyUI video as MP4 in memory, keeping the streams of an MP4 source as they are."""
    buffer = io.BytesIO()
    try:
        video.save_to(buffer, format=Types.VideoContainer.MP4, codec=Types.VideoCodec.AUTO)  # pyright: ignore[reportUnknownMemberType] # reason: ComfyUI types its metadata parameter as a bare dict.
    except Exception:  # noqa: BLE001 # reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise KIEError(ErrorCode.MEDIA, VIDEO_UNWRITABLE) from None
    return _build_encoded(buffer.getvalue(), 'video')


def encode_local_file(file: KIEFile) -> EncodedFile:
    """Encode one local file from File: Add, which holds one image or mask frame, one audio clip, or one video."""
    media = file.media
    if file.kind == 'image':
        return _encode_image(cast('torch.Tensor', media))
    if file.kind == 'mask':
        return _encode_mask(cast('torch.Tensor', media))
    if file.kind == 'audio':
        return _encode_audio(cast('Input.Audio', media))
    return _encode_video(cast('Input.Video', media))


def decode_images(contents: Sequence[bytes]) -> tuple[tuple[torch.Tensor, ...], tuple[torch.Tensor, ...]]:
    """Read each image as pixels [1, H, W, 3] and its mask [1, H, W], where the mask is 1 minus alpha.

    An opaque image gets a mask of zeros, so the masks pair with the images by index.
    """
    pixels: list[torch.Tensor] = []
    masks: list[torch.Tensor] = []
    for content in contents:
        try:
            image = bytesio_to_image_tensor(io.BytesIO(content))
        except Exception:  # noqa: BLE001 # reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
            raise KIEError(ErrorCode.MEDIA, IMAGE_UNREADABLE) from None
        if image.shape[-1] == IMAGE_TENSOR['RGBA_CHANNELS']:
            pixels.append(image[..., : IMAGE_TENSOR['RGB_CHANNELS']].contiguous())
            masks.append(1.0 - image[..., IMAGE_TENSOR['RGB_CHANNELS']])
        else:
            pixels.append(image)
            masks.append(torch.zeros(image.shape[:3], dtype=image.dtype))
    return tuple(pixels), tuple(masks)


def decode_video(content: bytes) -> Input.Video:
    """Read a video from memory, and its size once, so an unreadable file fails here and not in Save Video."""
    try:
        video = InputImpl.VideoFromFile(io.BytesIO(content))
        video.get_dimensions()
    except Exception:  # noqa: BLE001 # reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise KIEError(ErrorCode.MEDIA, VIDEO_UNREADABLE) from None
    return video


def decode_audio(content: bytes) -> Input.Audio:
    """Read any common audio container as ComfyUI audio: a waveform [1, C, T] and its sample rate."""
    try:
        audio = cast('Input.Audio', cast('object', audio_bytes_to_audio_input(content)))
    except Exception:  # noqa: BLE001 # reason: ComfyUI's helper raises unrelated exception types; one reviewed message replaces them.
        raise KIEError(ErrorCode.MEDIA, AUDIO_UNREADABLE) from None
    return audio


__all__ = ['decode_audio', 'decode_images', 'decode_video', 'encode_local_file']
