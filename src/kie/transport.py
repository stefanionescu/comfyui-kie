"""Open every HTTP session the extension uses, and send the only requests that carry the KIE API key.

The extension sends the request that creates a task once and never again. A request that bills nothing fails without a
charge.
"""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING
from contextlib import asynccontextmanager

from yarl import URL
import aiohttp
from pydantic import ValidationError

from .failures import build_failure
from ..config.kie import HOSTS, PAGES, REPLY_BYTES, SUCCESS_CODE
from ..config.units import BYTES_PER_MEGABYTE
from ..state.errors import KIEError, ErrorCode
from ..state.models import Envelope, ChatReply
from ..config.messages.run import READ_TIMEOUT, DOWNLOAD_LIMIT, KIE_UNREACHABLE, REPLY_UNREADABLE
from ..config.messages.tasks import CREATE_UNCERTAIN, OUTPUT_DOWNLOAD_FAILED

if TYPE_CHECKING:
    from collections.abc import Mapping, AsyncGenerator

    from ..state import Json
    from ..state.settings import Settings, Configuration
    from ..state.credentials import Credential


def _create_session(settings: Settings) -> aiohttp.ClientSession:
    """Open one session for one request, bounded by the request timeout.

    The session ignores the environment's proxy settings and every cookie, and no request follows a redirect, so
    neither the key nor a reply passes through another host.
    """
    timeout = aiohttp.ClientTimeout(total=settings.request_timeout_seconds)
    session = aiohttp.ClientSession(timeout=timeout, trust_env=False, cookie_jar=aiohttp.DummyCookieJar())
    # aiohttp sends a request again when its connection drops, and its only switch for that is private.
    setattr(session, '_retry_connection', False)  # noqa: B010 # reason: aiohttp offers no public switch for its resend.
    return session


def _build_headers(url: URL, credential: Credential | None) -> dict[str, str]:
    """Add the API key only for an https address on one of KIE's hosts, whatever address a reply named."""
    headers = {'Accept': 'application/json'}
    if credential is not None and url.scheme == 'https' and url.host in HOSTS.values():
        headers['Authorization'] = f'Bearer {credential.value}'
    return headers


async def _read_body(response: aiohttp.ClientResponse, settings: Settings) -> bytes:
    """Read a reply or a file within the maximum download size."""
    maximum = settings.max_download_megabytes
    content = bytearray()
    async for chunk in response.content.iter_chunked(REPLY_BYTES['CHUNK']):
        content.extend(chunk)
        if len(content) > maximum * BYTES_PER_MEGABYTE:
            raise KIEError(ErrorCode.MEDIA, DOWNLOAD_LIMIT.format(maximum=maximum))
    return bytes(content)


def _read_envelope(status: int, content: bytes) -> Json:
    """Return the result inside KIE's envelope, or the failure its code names.

    KIE answers most failures with HTTP 200 and an error code in the body. A body that is not an envelope takes its
    failure from the HTTP status, and is unreadable when the status says success.
    """
    try:
        envelope = Envelope.model_validate_json(content)
    except ValidationError:
        if status >= HTTPStatus.MULTIPLE_CHOICES:
            raise build_failure(status, None) from None
        raise KIEError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
    if envelope.code != SUCCESS_CODE:
        raise build_failure(envelope.code, envelope.msg)
    return envelope.payload


@asynccontextmanager
async def _send_free_request(
    method: str, url: URL, settings: Settings, *, credential: Credential | None, form: aiohttp.FormData | None = None
) -> AsyncGenerator[aiohttp.ClientResponse]:
    """Send one request that bills nothing, once, and hand over its reply.

    A failure to connect or to read counts as KIE being out of reach, never as a charge, because the request bills
    nothing.
    """
    headers = _build_headers(url, credential)
    session = _create_session(settings)
    try:
        async with (
            session,
            session.request(method, url, headers=headers, data=form, allow_redirects=False) as response,
        ):
            yield response
    except aiohttp.ClientError:
        raise KIEError(ErrorCode.TRANSPORT, KIE_UNREACHABLE) from None
    except TimeoutError:
        raise KIEError(ErrorCode.TIMEOUT, READ_TIMEOUT.format(seconds=settings.request_timeout_seconds)) from None


async def send_lookup(url: URL, configuration: Configuration) -> Json:
    """Send one read that bills nothing, such as a model read, and return the result inside KIE's envelope."""
    settings = configuration.settings
    async with _send_free_request('GET', url, settings, credential=configuration.credential) as response:
        status = response.status
        content = await _read_body(response, settings)
    return _read_envelope(status, content)


async def _send_paid_request(url: URL, body: Mapping[str, Json], configuration: Configuration) -> tuple[int, bytes]:
    """Send one paid request once, and return its HTTP status and body.

    A connection that fails before the request leaves bills nothing. A connection that breaks after it may have
    billed, so the message names the logs page to check before running again.
    """
    settings = configuration.settings
    headers = _build_headers(url, configuration.credential)
    session = _create_session(settings)
    try:
        async with session, session.post(url, json=body, headers=headers, allow_redirects=False) as response:
            status = response.status
            content = await _read_body(response, settings)
    except aiohttp.ClientConnectorError:
        raise KIEError(ErrorCode.TRANSPORT, KIE_UNREACHABLE) from None
    except (aiohttp.ClientError, TimeoutError):
        raise KIEError(ErrorCode.UNCERTAIN, CREATE_UNCERTAIN.format(logs=PAGES['LOGS'])) from None
    return status, content


async def send_task(url: URL, body: Mapping[str, Json], configuration: Configuration) -> str:
    """Send the request that creates a task, once, and return the ID of the task.

    A success without a task ID may still have created the task, so the message names the logs page too.
    """
    status, content = await _send_paid_request(url, body, configuration)
    reply = _read_envelope(status, content)
    task_id = reply.get('taskId') if isinstance(reply, dict) else None
    if not isinstance(task_id, str):
        raise KIEError(ErrorCode.UNCERTAIN, CREATE_UNCERTAIN.format(logs=PAGES['LOGS']))
    return task_id


async def send_chat(url: URL, body: Mapping[str, Json], configuration: Configuration) -> Json:
    """Send one paid chat request once, and return the reply as the format of the model writes it.

    A chat reply is not in KIE's envelope. A failure comes either as KIE's envelope with an error code, or, from Claude,
    as an error object with an HTTP status.
    """
    status, content = await _send_paid_request(url, body, configuration)
    try:
        reply = ChatReply.model_validate_json(content)
    except ValidationError:
        raise KIEError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
    if status >= HTTPStatus.MULTIPLE_CHOICES or (reply.code is not None and reply.code != SUCCESS_CODE):
        raise build_failure(reply.code or status, reply.msg or (reply.error.message if reply.error else None))
    return reply.model_dump(by_alias=True, exclude_unset=True)


async def send_upload(url: URL, form: aiohttp.FormData, configuration: Configuration) -> Json:
    """Upload one file to KIE's upload host with the key, and return the result inside KIE's envelope."""
    settings = configuration.settings
    async with _send_free_request('POST', url, settings, credential=configuration.credential, form=form) as response:
        status = response.status
        content = await _read_body(response, settings)
    return _read_envelope(status, content)


async def download_output(url: str, settings: Settings) -> bytes:
    """Download one file a task made, once, without any credential.

    The link may carry its own signature, so it goes out byte for byte.
    """
    async with _send_free_request('GET', URL(url, encoded=True), settings, credential=None) as response:
        if response.status >= HTTPStatus.MULTIPLE_CHOICES:
            raise KIEError(ErrorCode.TRANSPORT, OUTPUT_DOWNLOAD_FAILED.format(status=response.status))
        return await _read_body(response, settings)


__all__ = ['download_output', 'send_chat', 'send_lookup', 'send_task', 'send_upload']
