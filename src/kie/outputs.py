"""Find the files in a task's result."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast
from pathlib import PurePosixPath
from urllib.parse import urlsplit

from ..state.files import KIEFile
from ..config.media import LINK_SCHEME, OUTPUT_EXTENSIONS

if TYPE_CHECKING:
    from ..state import Json
    from ..state.files import FileKind


def _list_links(value: Json, links: list[str]) -> None:
    """Walk one value depth first, adding each https link once, in the order KIE wrote it."""
    if isinstance(value, dict):
        for item in value.values():
            _list_links(item, links)
    elif isinstance(value, list):
        for item in value:
            _list_links(item, links)
    elif isinstance(value, str) and urlsplit(value).scheme == LINK_SCHEME and value not in links:
        links.append(value)


def list_output_files(result: Json) -> tuple[KIEFile, ...]:
    """List every file in a task's result: each https link at any depth, sorted by kind by its extension.

    KIE gives files as bare links: resultUrls for most models, data[].audio_url for music, and lastFrameUrl beside a
    video. A link of another kind, such as a cover image beside a song, stays in the result.
    """
    links: list[str] = []
    _list_links(result, links)
    files: list[KIEFile] = []
    for link in links:
        extension = PurePosixPath(urlsplit(link).path).suffix.lower()
        kind = cast('FileKind', OUTPUT_EXTENSIONS.get(extension, 'other'))
        files.append(KIEFile(kind=kind, url=link, media=None, origin='output', field=None))
    return tuple(files)


__all__ = ['list_output_files']
