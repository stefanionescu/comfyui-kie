"""Own the private settings and API key changes, outside ComfyUI's public storage."""

import json
import hashlib
from pathlib import Path
import threading
from dataclasses import field, asdict, dataclass

from ..state import Json
from .schema import DEFAULT_SETTINGS, parse_settings
from ..state.errors import KIEError, ErrorCode
from ..state.parsing import parse_fields
from ..storage.files import read_file, save_file
from ..config.storage import FILE_NAMES, MAX_FILE_BYTES
from ..state.settings import Settings
from ..config.security import MAX_CREDENTIAL_CHARACTERS
from ..config.settings import SETTING_RANGES
from ..storage.credentials import parse_credential, read_credential_source
from ..config.messages.settings import SETTINGS_CHANGED, SETTING_READ_ONLY


@dataclass(slots=True)
class ConfigurationStore:
    """The private state folder, with one lock for settings and key changes across server and executor threads.

    Attributes:
        directory: The private state folder.
        lock: Serializes reads and writes of the settings and the key.

    """

    directory: Path
    lock: threading.Lock = field(default_factory=threading.Lock)

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
        return self.read_status()

    def delete_credential(self) -> dict[str, Json]:
        """Remove only the saved API key; a key in the server's environment stays in effect."""
        with self.lock:
            (self.directory / FILE_NAMES['CREDENTIAL']).unlink(missing_ok=True)
        return self.read_status()


__all__ = ['ConfigurationStore']
