"""The private settings and key that the local routes and the nodes share in one ComfyUI process."""

from ..storage.files import choose_state_directory
from ..settings.store import ConfigurationStore

# One store, so the routes and the nodes take turns on one lock, and a key change renews the nodes' cache token.
CONFIGURATION = ConfigurationStore(choose_state_directory())

__all__ = ['CONFIGURATION']
