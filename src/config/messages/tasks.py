"""Messages for the outcomes of a task: created, failed, timed out, or collected later."""

CREATE_UNCERTAIN = (
    'The connection to KIE broke after the task was sent, so it may still run and be billed. Check {logs} before '
    'running again.'
)

OUTPUT_DOWNLOAD_FAILED = (
    'A file the task made could not be downloaded (status {status}). Collect it with Task: Download.'
)

TASK_FAILED = 'The task failed on KIE, and was not billed: {reason} Change what it names, then run again.'

TASK_GONE = 'KIE no longer has this task or its files, so its record was deleted. Run the node that sent it again.'

TASK_UNKNOWN = (
    'Choose a recorded task in task. A paid KIE node records each task, and the list drops it once its outputs are '
    'collected.'
)

WAIT_LIMIT = (
    'The task did not finish within the request timeout of {seconds} seconds in KIE Settings. It keeps running on KIE '
    'and stays recorded. Collect it with Task: Download.'
)

__all__ = [
    'CREATE_UNCERTAIN',
    'OUTPUT_DOWNLOAD_FAILED',
    'TASK_FAILED',
    'TASK_GONE',
    'TASK_UNKNOWN',
    'WAIT_LIMIT',
]
