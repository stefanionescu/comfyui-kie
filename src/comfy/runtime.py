"""The private settings, key, and task records that the routes and the nodes share in one ComfyUI process."""

from ..storage.files import choose_state_directory
from ..config.storage import TASK_FILES
from ..settings.store import ConfigurationStore
from ..kie.tasks.records import TaskStore

# One store, so the routes and the nodes take turns on one lock, and a key change renews the nodes' cache token.
CONFIGURATION = ConfigurationStore(choose_state_directory())

# One store of task records, in the same private folder.
TASKS = TaskStore(CONFIGURATION.directory / TASK_FILES['FOLDER'])

__all__ = ['CONFIGURATION', 'TASKS']
