"""Read the KIE API key, and keep it out of public records."""

import os
from pathlib import Path

from .files import read_file
from ..state.errors import KIEError, ErrorCode
from ..config.storage import FILE_NAMES, ENVIRONMENT_VARIABLES
from ..config.security import MAX_CREDENTIAL_CHARACTERS
from ..state.credentials import Credential
from ..config.messages.settings import KEY_EMPTY, KEY_REQUIRED, KEY_UNREADABLE, KEY_WHITESPACE


def parse_credential(value: str) -> Credential:
    """Refuse an empty or oversized key, or one with spaces; KIE decides whether a key is valid.

    Args:
        value: The key as typed or as stored.

    Returns:
        The key as a credential.

    Raises:
        KIEError: When the key is empty, too long, or holds whitespace.

    """
    if not value or value != value.strip() or len(value) > MAX_CREDENTIAL_CHARACTERS:
        raise KIEError(ErrorCode.CONFIGURATION, KEY_EMPTY.format(maximum=MAX_CREDENTIAL_CHARACTERS))
    if any(character.isspace() for character in value):
        raise KIEError(ErrorCode.CONFIGURATION, KEY_WHITESPACE)
    return Credential(value)


def read_credential(directory: Path) -> Credential:
    """Read the key from the server's environment first, then from the private saved file.

    Args:
        directory: The private state folder that holds the saved key file.

    Returns:
        The key of the environment, or else the saved key.

    Raises:
        KIEError: When the saved file cannot be read, or no key is set.

    """
    if ENVIRONMENT_VARIABLES['KEY'] in os.environ:
        return parse_credential(os.environ[ENVIRONMENT_VARIABLES['KEY']])
    path = directory / FILE_NAMES['CREDENTIAL']
    if path.exists():
        try:
            return parse_credential(read_file(path, max_bytes=MAX_CREDENTIAL_CHARACTERS).decode('utf-8'))
        except (OSError, UnicodeError):
            raise KIEError(ErrorCode.CONFIGURATION, KEY_UNREADABLE) from None
    raise KIEError(ErrorCode.AUTHENTICATION, KEY_REQUIRED)


def read_credential_source(directory: Path) -> str:
    """Report where the key comes from; this reads no key and returns none.

    Args:
        directory: The private state folder that holds the saved key file.

    Returns:
        The word environment, saved, or missing.

    """
    if ENVIRONMENT_VARIABLES['KEY'] in os.environ:
        return 'environment'
    return 'saved' if (directory / FILE_NAMES['CREDENTIAL']).is_file() else 'missing'


__all__ = ['parse_credential', 'read_credential', 'read_credential_source']
