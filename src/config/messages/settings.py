"""Messages for private settings, the API key, and state storage."""

KEY_EMPTY = 'Enter a KIE API key of 1 to {maximum} characters without spaces at either end.'

KEY_REQUIRED = "Set your KIE API key in KIE Settings or in the server's KIE_API_KEY before running."

KEY_UNREADABLE = 'The saved KIE API key could not be read. Save the key again in KIE Settings.'

KEY_WHITESPACE = 'Remove spaces and line breaks from the KIE API key.'

PRIVATE_STATE_LOCATION = "Keep the KIE extension's private state outside ComfyUI, its package, and its media folders."

RUNTIME_NOT_READY = 'The KIE nodes are still loading. Wait for ComfyUI to finish starting, then run again.'

SETTINGS_CHANGED = 'The settings changed in another window. Reload the settings and try again.'

SETTINGS_RANGE = 'Choose each KIE setting within its range.'

SETTINGS_UNREADABLE = "The KIE extension's private settings could not be read. Check the state folder's permissions."

SETTINGS_WHOLE_NUMBERS = 'Enter whole numbers for the KIE settings.'

SETTING_READ_ONLY = 'That KIE setting cannot be changed here.'

SETTING_UNKNOWN = 'The KIE settings file has an unknown setting. Remove it or reset the settings.'

STATE_DIRECTORY_ABSOLUTE = 'Set KIE_COMFY_STATE_DIRECTORY to an absolute folder path.'

STATE_FILE_SIZE = 'A KIE state file is larger than expected. Check the state folder.'

STATE_UNREADABLE = (
    "The KIE extension's private state could not be read or written. Check the state folder's permissions."
)

__all__ = [
    'KEY_EMPTY',
    'KEY_REQUIRED',
    'KEY_UNREADABLE',
    'KEY_WHITESPACE',
    'PRIVATE_STATE_LOCATION',
    'RUNTIME_NOT_READY',
    'SETTINGS_CHANGED',
    'SETTINGS_RANGE',
    'SETTINGS_UNREADABLE',
    'SETTINGS_WHOLE_NUMBERS',
    'SETTING_READ_ONLY',
    'SETTING_UNKNOWN',
    'STATE_DIRECTORY_ABSOLUTE',
    'STATE_FILE_SIZE',
    'STATE_UNREADABLE',
]
