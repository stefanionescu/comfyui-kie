"""The settings a request reads, and the snapshot of settings and key that one request uses."""

from dataclasses import field, dataclass

from .credentials import Credential


@dataclass(frozen=True, slots=True)
class Settings:
    """Limits that a workflow cannot raise.

    Attributes:
        request_timeout_seconds: How long one HTTP exchange may take, and the whole wait for a task.
        max_upload_megabytes: The largest single file the extension uploads to KIE.
        max_download_megabytes: The largest reply body or output file the extension accepts.

    """

    request_timeout_seconds: int
    max_upload_megabytes: int
    max_download_megabytes: int


@dataclass(frozen=True, slots=True)
class Configuration:
    """The settings and the API key that one request reads together.

    Attributes:
        settings: The limits in effect.
        credential: The KIE API key, left out of representations.
        generation: A token that names the API key in ComfyUI's cache.

    """

    settings: Settings
    credential: Credential = field(repr=False)
    generation: str


__all__ = ['Configuration', 'Settings']
