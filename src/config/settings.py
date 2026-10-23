"""The editable settings with their defaults and ranges, and the size and time a settings request may take."""

# Each setting's default and range, in seconds or in megabytes of 1,000,000 bytes. The largest input KIE's models
# document is a 100 MB video, so the upload limit stops there.
SETTING_RANGES: dict[str, dict[str, int]] = {
    'request_timeout_seconds': {'default': 1800, 'minimum': 10, 'maximum': 3600},
    'max_upload_megabytes': {'default': 100, 'minimum': 1, 'maximum': 100},
    'max_download_megabytes': {'default': 512, 'minimum': 16, 'maximum': 4096},
}

# The settings route reads a request body of at most max_bytes, in chunks, within timeout_seconds.
SETTINGS_BODY = {
    'MAX_BYTES': 4096,
    'CHUNK_BYTES': 1024,
    'TIMEOUT_SECONDS': 5,
}

__all__ = [
    'SETTINGS_BODY',
    'SETTING_RANGES',
]
