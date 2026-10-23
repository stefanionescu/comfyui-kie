"""Run one task: build its input, upload its files, create it once, record it, wait for it, and collect its files.

KIE has no cancel for a task. A ComfyUI cancel stops only the wait. The task keeps running and KIE bills it, and its
record lets Task: Download collect it.
"""

from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING, cast
import asyncio
from datetime import UTC, datetime
from dataclasses import dataclass

from yarl import URL
from pydantic import ValidationError

from ..models import read_kie_model
from ..outputs import list_output_files
from ..uploads import upload_files
from ..failures import clean_reason
from ..arguments import build_input
from ..transport import send_json, send_lookup, download_output
from ...config.kie import HOSTS, PAGES, ROUTES
from ...state.tasks import TaskState, OutputFile, TaskRecord, TaskResult
from ...config.tasks import STATES, POLL_SECONDS, PROGRESS_STEPS, RECORD_VERSION, RECORD_RETENTION_SECONDS
from ...state.errors import KIEError, ErrorCode
from ...config.messages.run import REPLY_UNREADABLE
from ...config.messages.tasks import TASK_GONE, WAIT_LIMIT, TASK_FAILED, CREATE_UNCERTAIN

if TYPE_CHECKING:
    from collections.abc import Callable

    from ...state import Json
    from .records import TaskStore
    from ...state.files import KIEFile, FileKind, EncodedFile
    from ...state.tasks import Progress, TaskRequest
    from ...state.models import Kind, KIEModel
    from ...state.settings import Configuration

_API = URL.build(scheme='https', host=HOSTS['API'])


@dataclass(frozen=True, slots=True)
class TaskWait:
    """What a wait for a task needs besides the task's record.

    Attributes:
        tasks: The task records, which a finished or gone task leaves.
        configuration: The settings and the key.
        progress: The progress bar of the node, or None.
        download_kinds: The kinds of file the node decodes, the only ones downloaded.

    """

    tasks: TaskStore
    configuration: Configuration
    progress: Progress
    download_kinds: frozenset[FileKind]


async def _create_task(model: KIEModel, task_input: dict[str, Json], kind: Kind, wait: TaskWait) -> TaskRecord:
    """Create the task once, and record it before the first wait.

    A cancel cannot cut the create short. Once the request leaves, the extension waits for the reply and records the
    task, and only then lets the cancel through, so Task: Download can still collect the task.
    """
    body: dict[str, Json] = {'model': model.entry.model, 'input': task_input}
    sending = asyncio.ensure_future(send_json(_API.with_path(ROUTES['CREATE_TASK']), body, wait.configuration))
    is_cancelled = False
    while not sending.done():
        try:
            await asyncio.shield(sending)
        except asyncio.CancelledError:
            is_cancelled = True
    reply = sending.result()
    task_id = reply.get('taskId') if isinstance(reply, dict) else None
    if not isinstance(task_id, str):
        raise KIEError(ErrorCode.UNCERTAIN, CREATE_UNCERTAIN.format(logs=PAGES['LOGS']))
    submitted_at = datetime.now(UTC).isoformat(timespec='seconds')
    record = TaskRecord(
        version=RECORD_VERSION, task_id=task_id, model=model.entry.model, kind=kind, submitted_at=submitted_at
    )
    await asyncio.to_thread(wait.tasks.save, record)
    if is_cancelled:
        raise asyncio.CancelledError
    return record


async def _read_state(record: TaskRecord, wait: TaskWait) -> TaskState:
    """Read the state of the task once; a task that KIE does not know deletes its record."""
    url = _API.with_path(ROUTES['RECORD_INFO']).with_query({'taskId': record.task_id})
    try:
        reply = await send_lookup(url, wait.configuration)
    except KIEError as error:
        if error.code is not ErrorCode.INVALID_INPUT:
            raise
        await asyncio.to_thread(wait.tasks.delete, record.task_id)
        raise KIEError(ErrorCode.UNAVAILABLE, TASK_GONE) from None
    try:
        return TaskState.model_validate(reply)
    except ValidationError:
        raise KIEError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None


async def _wait_for_end(record: TaskRecord, wait: TaskWait) -> TaskState:
    """Read the state of the task every few seconds until it ends, within the request timeout.

    On a timeout the record stays, so Task: Download can collect the task later.
    """
    seconds = wait.configuration.settings.request_timeout_seconds
    deadline = time.monotonic() + seconds
    is_running = False
    while True:
        state = await _read_state(record, wait)
        if state.state in {STATES['SUCCESS'], STATES['FAIL']}:
            return state
        if state.state == STATES['RUNNING'] and not is_running and wait.progress is not None:
            is_running = True
            await wait.progress(PROGRESS_STEPS['RUNNING'])
        if time.monotonic() + POLL_SECONDS > deadline:
            raise KIEError(ErrorCode.TIMEOUT, WAIT_LIMIT.format(seconds=seconds))
        await asyncio.sleep(POLL_SECONDS)


async def collect_task(
    record: TaskRecord,
    tasks: TaskStore,
    download_kinds: frozenset[FileKind],
    configuration: Configuration,
    progress: Progress,
) -> TaskResult:
    """Wait for a recorded task to end, download the files the node decodes, and delete the record.

    A failed task bills nothing and deletes its record. A record older than KIE keeps files goes, unread.
    """
    wait = TaskWait(tasks, configuration, progress, download_kinds)
    submitted = datetime.fromisoformat(record.submitted_at)
    if (datetime.now(UTC) - submitted).total_seconds() > RECORD_RETENTION_SECONDS:
        await asyncio.to_thread(wait.tasks.delete, record.task_id)
        raise KIEError(ErrorCode.UNAVAILABLE, TASK_GONE)
    state = await _wait_for_end(record, wait)
    if state.state == STATES['FAIL']:
        await asyncio.to_thread(wait.tasks.delete, record.task_id)
        raise KIEError(ErrorCode.REFUSED, TASK_FAILED.format(reason=clean_reason(state.fail_msg)))
    try:
        result: Json = json.loads(state.result_json or '{}')
    except ValueError:
        raise KIEError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
    settings = wait.configuration.settings
    outputs: list[OutputFile] = []
    for file in list_output_files(result):
        link = file.url if file.kind in wait.download_kinds else None
        outputs.append(OutputFile(file, await download_output(link, settings) if link is not None else None))
    if wait.progress is not None:
        await wait.progress(PROGRESS_STEPS['DOWNLOADED'])
    await asyncio.to_thread(wait.tasks.delete, record.task_id)
    return TaskResult(record=record, result=result, files=tuple(outputs))


async def run_task(
    request: TaskRequest,
    encode: Callable[[KIEFile], EncodedFile],
    tasks: TaskStore,
    configuration: Configuration,
    progress: Progress,
) -> TaskResult:
    """Check the request against the model, upload its files, create the task once, and collect it."""
    wait = TaskWait(tasks, configuration, progress, frozenset({cast('FileKind', request.kind)}))
    model = await read_kie_model(request.model_id, request.kind, configuration)
    values = build_input(model, request.texts, request.settings, request.arguments, request.files)
    task_input = await upload_files(values, encode, wait.configuration)
    if wait.progress is not None:
        await wait.progress(PROGRESS_STEPS['UPLOADED'])
    record = await _create_task(model, task_input, request.kind, wait)
    if wait.progress is not None:
        await wait.progress(PROGRESS_STEPS['CREATED'])
    return await collect_task(record, tasks, wait.download_kinds, configuration, progress)


__all__ = ['collect_task', 'run_task']
