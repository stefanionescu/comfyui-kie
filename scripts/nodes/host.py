"""The ComfyUI nodes the example workflows place beside this extension's own."""

from enum import StrEnum


class HostNode(StrEnum):
    """One ComfyUI node, by the name ComfyUI registers it under.

    Attributes:
        AUDIO: The node that loads an audio file.
        IMAGE: The node that loads an image file.
        PREVIEW: The node that previews any value.
        TEXT: The node that holds one line of text.
        TEXT_BLOCK: The node that holds a text of several lines.
        FORMAT: The node that formats a text.
        LIST_ITEM: The node that takes one item from a list.
        SAVE_IMAGE: The node that saves an image.
        PREVIEW_IMAGE: The node that previews an image.
        JOIN_ALPHA: The node that joins an image with an alpha channel.
        SAVE_TEXT: The node that saves a text.
        SAVE_AUDIO: The node that saves audio.
        MERGE_AUDIO: The node that merges audio.
        SAVE_VIDEO: The node that saves a video.

    """

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
