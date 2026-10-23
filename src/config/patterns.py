"""Patterns that the extension matches text against; each module that uses one compiles it once."""

# A settings revision: the SHA-256 of the saved settings, in lowercase hexadecimal.
REVISION_PATTERN = r'^[a-f0-9]{64}$'

__all__ = ['REVISION_PATTERN']
