"""Errors whose messages a person can read without exposing provider data."""

from enum import StrEnum


class ErrorCode(StrEnum):
    """Stable categories for the messages a person reads."""

    CONFIGURATION = 'configuration'
    AUTHENTICATION = 'authentication'
    CREDITS = 'credits'
    INVALID_INPUT = 'invalid_input'
    REFUSED = 'refused'
    UNAVAILABLE = 'unavailable'
    RATE_LIMITED = 'rate_limited'
    TIMEOUT = 'timeout'
    TRANSPORT = 'transport'
    UNCERTAIN = 'uncertain'
    INTERRUPTED = 'interrupted'
    CONFLICT = 'conflict'
    MEDIA = 'media'


class KIEError(RuntimeError):
    """A reviewed message; when KIE gave a reason, the message already holds its cleaned text.

    Attributes:
        code: The category of the failure.

    """

    def __init__(self, code: ErrorCode, message: str) -> None:
        """Keep the complete message and its category."""
        super().__init__(message)
        self.code = code


__all__ = ['ErrorCode', 'KIEError']
