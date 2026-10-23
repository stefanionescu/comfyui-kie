"""Register the extension's local routes with ComfyUI."""

from pathlib import Path

from server import PromptServer
import folder_paths
from comfy.cli_args import args

from .runtime import CONFIGURATION
from ..state.errors import KIEError, ErrorCode
from ..settings.routes import ConfigurationRoutes
from ..config.messages.settings import PRIVATE_STATE_LOCATION

# The installed extension, which the private state must stay out of.
_EXTENSION_ROOT = Path(__file__).resolve().parents[2]


def register_routes() -> None:
    """Refuse a state folder inside ComfyUI or the extension, then register every local route."""
    directory = CONFIGURATION.directory.resolve()
    public_roots = (
        folder_paths.base_path,
        folder_paths.get_input_directory(),
        folder_paths.get_output_directory(),
        folder_paths.get_temp_directory(),
        folder_paths.get_user_directory(),
        str(_EXTENSION_ROOT),
    )
    if any(directory.is_relative_to(Path(root).resolve()) for root in public_roots):
        raise KIEError(ErrorCode.CONFIGURATION, PRIVATE_STATE_LOCATION)
    ConfigurationRoutes(CONFIGURATION, is_multi_user=args.multi_user).register(PromptServer.instance.routes)


__all__ = ['register_routes']
