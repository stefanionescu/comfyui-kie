"""How the extension creates, records, waits for, and lists a task."""

# How often the extension reads a running task's state, in seconds; KIE allows 10 reads a second for each task.
POLL_SECONDS = 3

# The task states KIE reports. A task in neither final state is still waiting or running.
STATES = {
    'RUNNING': 'generating',
    'SUCCESS': 'success',
    'FAIL': 'fail',
}

# The version of the file of a task record; the store skips a record of another version.
RECORD_VERSION = 1

# KIE keeps the files of a task for 14 days, so Task: Download cannot collect an older record.
RECORD_RETENTION_SECONDS = 14 * 24 * 60 * 60

# The upload folder name on KIE's upload host.
UPLOAD_PATH = 'comfyui'

# Task: Download lists each record as its task ID, model, and start time, joined by this, with the time cut to minutes.
LABEL_SEPARATOR = ' · '
LABEL_TIME_CHARACTERS = 16

# A progress bar of five steps: files uploaded, task created, model running, outputs downloaded, outputs built.
PROGRESS_STEPS = {
    'UPLOADED': 1,
    'CREATED': 2,
    'RUNNING': 3,
    'DOWNLOADED': 4,
    'TOTAL': 5,
}

__all__ = [
    'LABEL_SEPARATOR',
    'LABEL_TIME_CHARACTERS',
    'POLL_SECONDS',
    'PROGRESS_STEPS',
    'RECORD_RETENTION_SECONDS',
    'RECORD_VERSION',
    'STATES',
    'UPLOAD_PATH',
]
