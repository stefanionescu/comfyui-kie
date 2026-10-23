"""Check the private limits before the extension sends any request."""

from dataclasses import fields

from ..state import Json
from ..state.errors import KIEError, ErrorCode
from ..state.settings import Settings
from ..config.settings import SETTING_RANGES
from ..config.messages.settings import SETTINGS_RANGE, SETTING_UNKNOWN, SETTINGS_WHOLE_NUMBERS

# The default of every setting.
DEFAULT_SETTINGS = Settings(**{name: definition['default'] for name, definition in SETTING_RANGES.items()})


def parse_settings(document: dict[str, Json]) -> Settings:
    """Refuse unknown settings, so a misspelled limit never passes silently, and keep each limit in its range."""
    expected = {item.name for item in fields(Settings)}
    if document.keys() - expected:
        raise KIEError(ErrorCode.CONFIGURATION, SETTING_UNKNOWN)
    integers: dict[str, int] = {}
    for name in expected:
        value = document.get(name, getattr(DEFAULT_SETTINGS, name))
        if type(value) is not int:
            raise KIEError(ErrorCode.CONFIGURATION, SETTINGS_WHOLE_NUMBERS)
        definition = SETTING_RANGES[name]
        if not definition['minimum'] <= value <= definition['maximum']:
            raise KIEError(ErrorCode.CONFIGURATION, SETTINGS_RANGE)
        integers[name] = value
    return Settings(**integers)


__all__ = ['DEFAULT_SETTINGS', 'parse_settings']
