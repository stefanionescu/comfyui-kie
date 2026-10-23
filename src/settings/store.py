"""Own the private settings and API key changes, outside ComfyUI's public storage."""

import json
import hashlib
from pathlib import Path
import secrets
import threading
from dataclasses import field, asdict, dataclass

from ..state import Json
from .schema import DEFAULT_SETTINGS, parse_settings
from ..state.errors import KIEError, ErrorCode
from ..state.parsing import parse_fields
from ..storage.files import read_file, save_file
from ..config.storage import FILE_NAMES, MAX_FILE_BYTES
from ..state.settings import Settings, Configuration
from ..config.security import GENERATION_TOKEN_BYTES, MAX_CREDENTIAL_CHARACTERS
from ..config.settings import SETTING_RANGES
from ..storage.credentials import read_credential, parse_credential, read_credential_source
from ..config.messages.settings import SETTINGS_CHANGED, SETTING_READ_ONLY, SETTINGS_UNREADABLE


@dataclass(slots=True)
class ConfigurationStore:
    """The private state folder, with one lock for settings and key changes across server and executor threads.

    Attributes:
        directory: The private state folder.
        lock: Serializes reads and writes of the settings and the key.

    """

    directory: Path
    lock: threading.Lock = field(default_factory=threading.Lock)
    # The last configuration a request read; None after the key changes, or after a read fails.
    _previous: Configuration | None = field(default=None, init=False, repr=False)

    def _read_settings(self) -> tuple[Settings, str]:
        """Read the settings and their revision, and create no file or folder.

        A save replaces the file whole, so a read needs no lock. The revision is the SHA-256 of the settings, so a stale
        window cannot overwrite newer changes.
        """
        path = self.directory / FILE_NAMES['SETTINGS']
        settings = DEFAULT_SETTINGS
        if path.exists():
            settings = parse_settings(parse_fields(read_file(path, max_bytes=MAX_FILE_BYTES['SETTINGS']).decode()))
        encoded = json.dumps(asdict(settings), sort_keys=True, separators=(',', ':')).encode()
        return settings, hashlib.sha256(encoded).hexdigest()

    def read_configuration(self) -> Configuration:
        """Read the settings and the key together for one request.

        The cache token stays while the key stays, and changes with the key, so a new key runs nodes again. No
        setting changes a successful result, and ComfyUI never caches a failed run, so a settings change keeps it.
        """
        with self.lock:
            try:
                settings, _revision = self._read_settings()
                credential = read_credential(self.directory)
            except (OSError, UnicodeError):
                self._previous = None
                raise KIEError(ErrorCode.CONFIGURATION, SETTINGS_UNREADABLE) from None
            except KIEError:
                self._previous = None
                raise
            previous = self._previous
            generation = secrets.token_hex(GENERATION_TOKEN_BYTES)
            if previous is not None and previous.credential == credential:
                generation = previous.generation
            self._previous = Configuration(settings, credential, generation)
            return self._previous

    def read_status(self) -> dict[str, Json]:
        """Describe the settings in effect and where the key comes from, without returning the key."""
        with self.lock:
            settings, revision = self._read_settings()
            source = read_credential_source(self.directory)
        return {
            'settings': asdict(settings),
            'setting_ranges': {
                name: {'minimum': definition['minimum'], 'maximum': definition['maximum']}
                for name, definition in SETTING_RANGES.items()
            },
            'credential_limit': MAX_CREDENTIAL_CHARACTERS,
            'revision': revision,
            'credential': {'source': source},
        }

    def save_settings(self, changes: dict[str, Json], revision: str) -> dict[str, Json]:
        """Apply checked changes only to the revision the dialog read."""
        if changes.keys() - set(SETTING_RANGES):
            raise KIEError(ErrorCode.CONFIGURATION, SETTING_READ_ONLY)
        with self.lock:
            current, current_revision = self._read_settings()
            if revision != current_revision:
                raise KIEError(ErrorCode.CONFLICT, SETTINGS_CHANGED)
            updated = parse_settings(asdict(current) | changes)
            save_file(self.directory / FILE_NAMES['SETTINGS'], (json.dumps(asdict(updated), indent=2) + '\n').encode())
        return self.read_status()

    def save_credential(self, value: str) -> dict[str, Json]:
        """Save a checked API key, and return only where the key in effect comes from."""
        credential = parse_credential(value)
        with self.lock:
            save_file(self.directory / FILE_NAMES['CREDENTIAL'], credential.value.encode('utf-8'))
            # A key saved again unchanged keeps the cache token, so it sends no second paid request.
            if self._previous is not None and self._previous.credential != credential:
                self._previous = None
        return self.read_status()

    def delete_credential(self) -> dict[str, Json]:
        """Remove only the saved API key; a key in the server's environment stays in effect."""
        with self.lock:
            (self.directory / FILE_NAMES['CREDENTIAL']).unlink(missing_ok=True)
            self._previous = None
        return self.read_status()


__all__ = ['ConfigurationStore']
