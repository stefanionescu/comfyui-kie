"""The ComfyUI nodes the example workflows place beside this extension's own."""

from enum import StrEnum


class HostNode(StrEnum):
    """One ComfyUI node, by the name ComfyUI registers it under."""

    AUDIO = 'LoadAudio'
    IMAGE = 'LoadImage'
    PREVIEW = 'PreviewAny'
    TEXT = 'PrimitiveString'
    TEXT_BLOCK = 'PrimitiveStringMultiline'
    FORMAT = 'StringFormat'
    LIST_ITEM = 'GetItemFromList'
    SAVE_IMAGE = 'SaveImage'
    PREVIEW_IMAGE = 'PreviewImage'
    JOIN_ALPHA = 'JoinImageWithAlpha'
    SAVE_TEXT = 'SaveText'
    SAVE_AUDIO = 'SaveAudioAdvanced'
    MERGE_AUDIO = 'AudioMerge'
    SAVE_VIDEO = 'SaveVideo'


__all__ = ['HostNode']
