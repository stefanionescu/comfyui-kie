"""Keep a private record of every task KIE accepted.

A task keeps running after a cancel, a timeout, or a ComfyUI restart, and its record lets Task: Download collect it.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
import threading
from dataclasses import field, dataclass

from pydantic import ValidationError

from ...state.tasks import TaskRecord
from ...config.tasks import LABEL_SEPARATOR, LABEL_TIME_CHARACTERS
from ...state.errors import KIEError, ErrorCode
from ...storage.files import read_file, save_file
from ...config.storage import TASK_FILES, MAX_FILE_BYTES
from ...config.patterns import TASK_ID_PATTERN
from ...config.messages.tasks import TASK_UNKNOWN

if TYPE_CHECKING:
    from pathlib import Path

_TASK_ID = re.compile(TASK_ID_PATTERN)


@dataclass(slots=True)
class TaskStore:
    """The task records folder. Every method blocks, so callers run it off the event loop.

    Attributes:
        directory: The private folder of the task records.

    """

    directory: Path
    # One lock for the folder's files, across the server's and the executor's threads.
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def _read_all(self) -> list[TaskRecord]:
        """Read every record, and skip a damaged, oversized, or other-version file, so it never blocks the rest."""
        if not self.directory.is_dir():
            return []
        records: list[TaskRecord] = []
        for path in sorted(self.directory.glob(f'*{TASK_FILES["SUFFIX"]}')):
            try:
                records.append(TaskRecord.model_validate_json(read_file(path, max_bytes=MAX_FILE_BYTES['TASK'])))
            except (OSError, ValidationError, KIEError):
                continue
        return records

    def save(self, record: TaskRecord) -> None:
        """Write one record atomically, named by its task ID."""
        path = self.directory / f'{record.task_id}{TASK_FILES["SUFFIX"]}'
        content = (record.model_dump_json(indent=2) + '\n').encode()
        with self._lock:
            save_file(path, content)

    def delete(self, task_id: str) -> None:
        """Delete one record; a record already gone needs nothing. Refuse an ID that cannot be a task ID."""
        if _TASK_ID.match(task_id) is None:
            raise KIEError(ErrorCode.INVALID_INPUT, TASK_UNKNOWN)
        path = self.directory / f'{task_id}{TASK_FILES["SUFFIX"]}'
        with self._lock:
            path.unlink(missing_ok=True)

    def read(self, task_id: str) -> TaskRecord:
        """Return the record of this task, and refuse an ID that cannot be a task ID, or that has no record."""
        if _TASK_ID.match(task_id) is None:
            raise KIEError(ErrorCode.INVALID_INPUT, TASK_UNKNOWN)
        with self._lock:
            record = next((record for record in self._read_all() if record.task_id == task_id), None)
        if record is None:
            raise KIEError(ErrorCode.INVALID_INPUT, TASK_UNKNOWN)
        return record

    def list_labels(self) -> list[str]:
        """List the records as Task: Download shows them, newest first: task ID, model, and start time in UTC.

        The label cuts the time to the minute and starts with the task ID, so the node can read the ID back.
        """
        with self._lock:
            records = sorted(self._read_all(), key=lambda record: record.submitted_at, reverse=True)
        return [
            LABEL_SEPARATOR.join(
                (record.task_id, record.model, record.submitted_at[:LABEL_TIME_CHARACTERS].replace('T', ' '))
            )
            for record in records
        ]


__all__ = ['TaskStore']
