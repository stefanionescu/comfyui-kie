"""The private state folder, its files and their size limits, and the environment variables that set them."""

# The API key in the server's environment, which takes precedence over the saved key, and an absolute folder that
# replaces the platform's own state folder.
ENVIRONMENT_VARIABLES = {
    'KEY': 'KIE_API_KEY',
    'STATE_DIRECTORY': 'KIE_COMFY_STATE_DIRECTORY',
}

# The state folder's name on macOS and Windows, and under XDG_STATE_HOME elsewhere.
STATE_FOLDER_NAMES = {
    'DEFAULT': 'KIEComfyUI',
    'XDG': 'kie-comfy',
}

# Only the folder's owner may open it.
PRIVATE_FOLDER_MODE = 0o700

# The extension writes a file under this prefix, then moves it into place.
TEMPORARY_PREFIX = '.kie-'

# The settings and the saved API key.
FILE_NAMES = {
    'SETTINGS': 'settings.json',
    'CREDENTIAL': 'credential',
}

# The largest settings file and task record the extension reads.
MAX_FILE_BYTES = {
    'SETTINGS': 65_536,
    'TASK': 16_384,
}

# The task records: one file per task ID, in this folder of the state folder.
TASK_FILES = {
    'FOLDER': 'tasks',
    'SUFFIX': '.json',
}

__all__ = [
    'ENVIRONMENT_VARIABLES',
    'FILE_NAMES',
    'MAX_FILE_BYTES',
    'PRIVATE_FOLDER_MODE',
    'STATE_FOLDER_NAMES',
    'TASK_FILES',
    'TEMPORARY_PREFIX',
]
