"""Files a KIE model reads or makes: a link or local media, and an encoded upload."""

from typing import Literal
from dataclasses import dataclass

from pydantic import Field

from . import Json, Reply

# What a file holds: one kind of media, or other for a file no node decodes.
type FileKind = Literal['image', 'mask', 'video', 'audio', 'other']
# Where a file comes from: a task's output, a link someone typed, or ComfyUI media to upload.
type FileOrigin = Literal['output', 'link', 'local']


@dataclass(frozen=True, slots=True)
class KIEFile:
    """One file a model input takes or a task makes: a link, or ComfyUI media that a request uploads.

    Attributes:
        kind: image, mask, video, audio, or other.
        url: The https link; None for local media.
        media: One image or mask frame, one audio clip, or a `VIDEO`, for local media; None for a link.
        origin: output, link, or local.
        field: The input File: Add names it for, such as image_urls; None until File: Add sets one.

    """

    kind: FileKind
    url: str | None
    media: object | None
    origin: FileOrigin
    field: str | None


@dataclass(frozen=True, slots=True)
class EncodedFile:
    """One local file, encoded, and ready to upload.

    Attributes:
        content: The file's bytes.
        content_type: Its media type.
        file_name: The name it takes on the upload host: its kind and the start of its digest.
        digest: The SHA-256 of the content, which finds a second copy of the same file in one request.

    """

    content: bytes
    content_type: str
    file_name: str
    digest: str


class UploadReply(Reply):
    """What KIE's upload host returns for one file.

    Attributes:
        download_url: The public link to put in a task's input; KIE names it downloadUrl.

    """

    download_url: str = Field(alias='downloadUrl')


# One input of a task as the checks build it: a JSON value, one file for a text input, or files for a list input.
type FieldValue = Json | KIEFile | tuple[KIEFile, ...]

# Other modules import the type aliases by name; __all__ lists the runtime names.
__all__ = ['EncodedFile', 'KIEFile', 'UploadReply']
