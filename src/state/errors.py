"""Errors whose messages a person can read without exposing provider data."""

from enum import StrEnum


class ErrorCode(StrEnum):
    """Stable categories for the messages a person reads.

    Attributes:
        CONFIGURATION: The settings or the key of the extension are wrong or cannot be read.
        AUTHENTICATION: KIE does not accept the key.
        CREDITS: The account has too few credits.
        INVALID_INPUT: An input of the request is not valid.
        REFUSED: KIE refused the request.
        UNAVAILABLE: The service or the model is not available.
        RATE_LIMITED: Too many requests arrived in a short time.
        TIMEOUT: The work did not finish in time.
        TRANSPORT: The connection failed.
        UNCERTAIN: The outcome of a request is not known.
        INTERRUPTED: The run was stopped before it finished.
        CONFLICT: The saved state changed after it was read.
        MEDIA: A media file cannot be read or used.

    """

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
    """A reviewed message; when KIE gave a reason, the message already holds its cleaned text."""

    def __init__(self, code: ErrorCode, message: str) -> None:
        """Keep the complete message and its category.

        Args:
            code: The category of the failure.
            message: The complete message a person reads.

        """
        super().__init__(message)
        self.code = code


__all__ = ['ErrorCode', 'KIEError']
