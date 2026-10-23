"""Patterns that the extension matches text against; each module that uses one compiles it once."""

# A settings revision: the SHA-256 of the saved settings, in lowercase hexadecimal.
REVISION_PATTERN = r'^[a-f0-9]{64}$'

# A KIE model ID: names of letters, digits, dots, dashes, and underscores, joined by slashes, such as wan/3-0-video.
MODEL_ID_PATTERN = r'^[A-Za-z0-9][A-Za-z0-9._-]*(/[A-Za-z0-9][A-Za-z0-9._-]*)*$'

# The name of a model input that File: Add names: letters, digits, and underscores, such as image_urls.
FIELD_NAME_PATTERN = r'^[A-Za-z_][A-Za-z0-9_]*$'

# A KIE task ID: letters, digits, dashes, and underscores.
TASK_ID_PATTERN = r'^[A-Za-z0-9_-]{1,128}$'

# Text a reason from KIE must not carry: links, and anything shaped like a key.
REASON_PATTERNS = {
    'URL': r'https?://\S+',
    'KEY': r'\b[A-Za-z0-9_-]{32,}\b',
}

__all__ = ['FIELD_NAME_PATTERN', 'MODEL_ID_PATTERN', 'REASON_PATTERNS', 'REVISION_PATTERN', 'TASK_ID_PATTERN']
