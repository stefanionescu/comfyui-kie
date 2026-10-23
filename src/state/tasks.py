"""KIE tasks: the record kept while one runs, the request a node makes, and what a task made."""

from typing import Literal
from dataclasses import dataclass
from collections.abc import Mapping, Callable, Awaitable

from pydantic import Field

from . import Json, Reply, Value
from .files import KIEFile
from .models import Kind

# Reports one step of the progress bar of a node; None for a node that another node or pack calls.
type Progress = Callable[[int], Awaitable[None]] | None


class TaskRecord(Value):
    """One task KIE accepted, recorded before the first wait, so Task: Download can collect a task that keeps running.

    Attributes:
        version: The file format version; the store skips any other.
        task_id: KIE's task ID, which also names the record's file.
        model: The model the task runs.
        kind: The kind of node that sent it.
        submitted_at: When the node sent the task, as an ISO 8601 time in UTC.

    """

    version: Literal[1]
    task_id: str
    model: str
    kind: Kind
    submitted_at: str


class TaskState(Reply):
    """One read of a task's state.

    Attributes:
        task_id: KIE's task ID; KIE names it taskId.
        state: waiting, queuing, generating, success, or fail.
        result_json: The result as JSON text once the task succeeds; KIE names it resultJson.
        fail_code: KIE's code for a failed task; KIE names it failCode.
        fail_msg: KIE's reason for a failed task; KIE names it failMsg.

    """

    task_id: str = Field(alias='taskId')
    state: str
    result_json: str | None = Field(default=None, alias='resultJson')
    fail_code: str | None = Field(default=None, alias='failCode')
    fail_msg: str | None = Field(default=None, alias='failMsg')


@dataclass(frozen=True, slots=True)
class TaskRequest:
    """One task a paid node asks for, as its inputs came; the node reads and checks the model when it sends the task.

    Attributes:
        model_id: The model ID as typed, stripped.
        texts: The text boxes of the node, by input name, such as prompt.
        settings: The named inputs the person set, by KIE input name.
        arguments: The arguments input's JSON text.
        files: The files chain, each naming its input.
        kind: The kind of node that sends it.

    """

    model_id: str
    texts: Mapping[str, str]
    settings: Mapping[str, Json]
    arguments: str
    files: tuple[KIEFile, ...]
    kind: Kind


@dataclass(frozen=True, slots=True)
class OutputFile:
    """One file a task made.

    Attributes:
        file: The file and its link.
        content: The downloaded bytes, or None for a file no output of the node decodes.

    """

    file: KIEFile
    content: bytes | None


@dataclass(frozen=True, slots=True)
class TaskResult:
    """What one finished task made.

    Attributes:
        record: The task's record.
        result: The task's result, as KIE returned it.
        files: Every file in the result, in result order.

    """

    record: TaskRecord
    result: Json
    files: tuple[OutputFile, ...]


# Other modules import the type aliases by name; __all__ lists the runtime names.
__all__ = ['OutputFile', 'TaskRecord', 'TaskRequest', 'TaskResult', 'TaskState']
