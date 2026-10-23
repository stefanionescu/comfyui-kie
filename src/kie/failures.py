"""Turn KIE's error codes into reviewed messages that carry KIE's cleaned reason."""

import re

from ..config.kie import PAGES, REASON_ENDINGS, MAX_REASON_CHARACTERS
from ..state.errors import KIEError, ErrorCode
from ..config.patterns import REASON_PATTERNS
from ..config.messages.run import (
    KEY_LIMIT,
    NO_REASON,
    NOT_FOUND,
    CREDITS_LOW,
    MAINTENANCE,
    RESULT_LATE,
    KEY_REJECTED,
    RATE_LIMITED,
    SWITCHED_OFF,
    SERVER_FAILED,
    REQUEST_REJECTED,
    GENERATION_FAILED,
)

_URL = re.compile(REASON_PATTERNS['URL'])
_KEY = re.compile(REASON_PATTERNS['KEY'])

# The category and message of each code KIE documents. Any other code is a server failure.
_FAILURES: dict[int, tuple[ErrorCode, str]] = {
    401: (ErrorCode.AUTHENTICATION, KEY_REJECTED),
    402: (ErrorCode.CREDITS, CREDITS_LOW),
    404: (ErrorCode.UNAVAILABLE, NOT_FOUND),
    408: (ErrorCode.TIMEOUT, RESULT_LATE),
    422: (ErrorCode.INVALID_INPUT, REQUEST_REJECTED),
    429: (ErrorCode.RATE_LIMITED, RATE_LIMITED),
    433: (ErrorCode.CREDITS, KEY_LIMIT),
    455: (ErrorCode.UNAVAILABLE, MAINTENANCE),
    501: (ErrorCode.REFUSED, GENERATION_FAILED),
    505: (ErrorCode.UNAVAILABLE, SWITCHED_OFF),
}


def clean_reason(message: str | None) -> str:
    """Remove links and key-shaped text from KIE's reason, shorten it, and end it as a sentence.

    A link can be a public file address, so none stays. A message can add its next step after the reason.
    """
    text = ' '.join(_KEY.sub('', _URL.sub('', message or '')).split())
    if len(text) > MAX_REASON_CHARACTERS:
        text = text[: MAX_REASON_CHARACTERS - 1].rstrip() + '…'
    if text and not text.endswith(REASON_ENDINGS):
        text += '.'
    return text or NO_REASON


def build_failure(code: int, message: str | None) -> KIEError:
    """Build the reviewed error for one KIE code, with KIE's cleaned reason where the message has room for it."""
    category, template = _FAILURES.get(code, (ErrorCode.TRANSPORT, SERVER_FAILED))
    text = template.format(reason=clean_reason(message), keys=PAGES['KEYS'], billing=PAGES['BILLING'])
    return KIEError(category, text)


__all__ = ['build_failure', 'clean_reason']
