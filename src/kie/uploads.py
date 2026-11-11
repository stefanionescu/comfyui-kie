"""Upload the local files of one request to KIE's upload host, and put their links in the task's input.

Each request uploads its own files, and uploads the same file in two inputs of one request once. KIE deletes uploads
after 24 hours.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import asyncio

from yarl import URL
import aiohttp
from pydantic import ValidationError

from .transport import send_upload
from ..config.kie import HOSTS, ROUTES
from ..state.files import KIEFile, UploadReply
from ..config.tasks import UPLOAD_PATH
from ..config.units import BYTES_PER_MEGABYTE
from ..state.errors import KIEError, ErrorCode
from ..config.messages.run import REPLY_UNREADABLE
from ..config.messages.media import UPLOAD_LIMIT

if TYPE_CHECKING:
    from collections.abc import Mapping, Callable

    from ..state import Json
    from ..state.files import FieldValue, EncodedFile
    from ..state.settings import Configuration


async def _link_file(
    file: KIEFile, encode: Callable[[KIEFile], EncodedFile], links: dict[str, str], configuration: Configuration
) -> str:
    """Return a file's link: its own, or the link of its upload; links holds this request's uploads by digest.

    Args:
        file: The file an input of the task names.
        encode: Turns a local file into the bytes to upload.
        links: The links of the files this request uploaded, by digest; a new upload is added.
        configuration: The settings that hold the upload limit, and the key.

    Returns:
        The link KIE reads the file from.

    Raises:
        KIEError: When the file is over the upload limit, or the reply to the upload cannot be read.

    """
    if file.url is not None:
        return file.url
    encoded = await asyncio.to_thread(encode, file)
    maximum = configuration.settings.max_upload_megabytes
    if len(encoded.content) > maximum * BYTES_PER_MEGABYTE:
        size = round(len(encoded.content) / BYTES_PER_MEGABYTE, 1)
        raise KIEError(ErrorCode.MEDIA, UPLOAD_LIMIT.format(size=size, maximum=maximum))
    if encoded.digest not in links:
        form = aiohttp.FormData()
        form.add_field('file', encoded.content, filename=encoded.file_name, content_type=encoded.content_type)
        form.add_field('uploadPath', UPLOAD_PATH)
        form.add_field('fileName', encoded.file_name)
        url = URL.build(scheme='https', host=HOSTS['UPLOAD'], path=ROUTES['UPLOAD'])
        try:
            links[encoded.digest] = UploadReply.model_validate(await send_upload(url, form, configuration)).download_url
        except ValidationError:
            raise KIEError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
    return links[encoded.digest]


async def upload_files(
    values: Mapping[str, FieldValue], encode: Callable[[KIEFile], EncodedFile], configuration: Configuration
) -> dict[str, Json]:
    """Replace every file in a task's input with its link, uploading each local file once, in the input's order.

    Args:
        values: The input of the task by input name, where a file or a tuple of files stands for its link.
        encode: Turns a local file into the bytes to upload.
        configuration: The settings and the key of the uploads.

    Returns:
        The input of the task as JSON, with a link in place of every file.

    """
    links: dict[str, str] = {}
    task_input: dict[str, Json] = {}
    for name, value in values.items():
        if isinstance(value, KIEFile):
            task_input[name] = await _link_file(value, encode, links, configuration)
        elif isinstance(value, tuple):
            task_input[name] = [await _link_file(file, encode, links, configuration) for file in value]
        else:
            task_input[name] = value
    return task_input


__all__ = ['upload_files']
