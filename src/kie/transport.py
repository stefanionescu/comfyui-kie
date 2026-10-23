"""Open every HTTP session the extension uses, and send the only requests that carry the KIE API key."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import aiohttp
from pydantic import ValidationError

from .failures import build_failure
from ..config.kie import HOSTS, REPLY_BYTES, SUCCESS_CODE
from ..config.units import BYTES_PER_MEGABYTE
from ..state.errors import KIEError, ErrorCode
from ..state.models import Envelope
from ..config.messages.run import READ_TIMEOUT, DOWNLOAD_LIMIT, KIE_UNREACHABLE, REPLY_UNREADABLE

if TYPE_CHECKING:
    from yarl import URL

    from ..state import Json
    from ..state.settings import Settings, Configuration
    from ..state.credentials import Credential

# Every request asks for JSON.
_JSON_HEADERS = {'Accept': 'application/json'}


def _build_headers(url: URL, credential: Credential) -> dict[str, str]:
    """Add the API key only for an https address on one of KIE's hosts, whatever address a reply named."""
    headers = dict(_JSON_HEADERS)
    if url.scheme == 'https' and url.host in HOSTS.values():
        headers['Authorization'] = f'Bearer {credential.value}'
    return headers


async def _read_body(response: aiohttp.ClientResponse, settings: Settings) -> bytes:
    """Read a reply within the maximum download size."""
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
    failure from the HTTP status, or is unreadable when the status says success.
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


async def send_lookup(url: URL, configuration: Configuration) -> Json:
    """Send one read that bills nothing, such as a model read, and return the result inside KIE's envelope."""
    settings = configuration.settings
    headers = _build_headers(url, configuration.credential)
    # One session per request, bounded by the request timeout. It ignores the environment's proxy settings and every
    # cookie, and no request follows a redirect, so neither the key nor a reply passes through another host.
    session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=settings.request_timeout_seconds),
        trust_env=False,
        cookie_jar=aiohttp.DummyCookieJar(),
    )
    try:
        async with (
            session,
            session.get(url, headers=headers, allow_redirects=False) as response,
        ):
            status = response.status
            content = await _read_body(response, settings)
    except aiohttp.ClientError:
        raise KIEError(ErrorCode.TRANSPORT, KIE_UNREACHABLE) from None
    except TimeoutError:
        raise KIEError(ErrorCode.TIMEOUT, READ_TIMEOUT.format(seconds=settings.request_timeout_seconds)) from None
    return _read_envelope(status, content)


__all__ = ['send_lookup']
