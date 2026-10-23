"""Read one model from KIE before a node pays for a request, and keep it for the life of the process.

The reads are free, and need the API key. KIE gives them one shared budget of a request a second per account.
"""

from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING
import asyncio
import weakref
import threading
from dataclasses import field, dataclass

from yarl import URL
from pydantic import ValidationError

from .schema import parse_model
from .transport import send_lookup
from ..config.kie import HOSTS, PAGES, ROUTES
from ..state.errors import KIEError, ErrorCode
from ..state.models import CatalogPage
from ..config.models import KIND_NODES, DEFAULT_MODELS, READ_SPACING_SECONDS
from ..config.patterns import MODEL_ID_PATTERN
from ..config.messages.models import (
    KIND_NAMES,
    MODEL_FORM,
    MODEL_KIND,
    MODEL_EMPTY,
    MODEL_NO_KIND,
    MODEL_UNKNOWN,
    MODEL_READ_BUSY,
    MODEL_OTHER_ROUTE,
    MODEL_READ_UNREADABLE,
)

if TYPE_CHECKING:
    from ..state import Json
    from ..state.models import Kind, KIEModel
    from ..state.settings import Configuration

_MODEL_ID = re.compile(MODEL_ID_PATTERN)


@dataclass(slots=True)
class _ReadTurns:
    """When the next model read may start; the lock keeps two reads from taking one turn, across event loops.

    Attributes:
        lock: Serializes taking a turn.
        next_start: The monotonic time the next read may start.

    """

    lock: threading.Lock = field(default_factory=threading.Lock)
    next_start: float = 0.0


# The process keeps one schedule of reads, because KIE counts every read of the account against one budget.
_TURNS = _ReadTurns()
# The extension reads each model once per ComfyUI process; a failed read keeps nothing, so the next run reads again.
_MODELS: dict[str, KIEModel] = {}
# The reads in flight on each event loop, keyed by model ID, which callers asking at the same time share.
_READS: weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, dict[str, asyncio.Task[KIEModel]]] = (
    weakref.WeakKeyDictionary()
)


async def _read_in_turn(url: URL, configuration: Configuration) -> Json:
    """Read one free route in its turn; a rate limit waits for a later turn, within the request timeout."""
    deadline = time.monotonic() + configuration.settings.request_timeout_seconds
    while True:
        with _TURNS.lock:
            now = time.monotonic()
            start = max(now, _TURNS.next_start)
            _TURNS.next_start = start + READ_SPACING_SECONDS
        await asyncio.sleep(start - now)
        try:
            return await send_lookup(url, configuration)
        except KIEError as error:
            if error.code is not ErrorCode.RATE_LIMITED:
                raise
            if time.monotonic() > deadline:
                raise KIEError(ErrorCode.RATE_LIMITED, MODEL_READ_BUSY) from None


async def _download_model(model_id: str, configuration: Configuration) -> KIEModel:
    """Find the model in KIE's catalog with one search, then read its schema."""
    api = URL.build(scheme='https', host=HOSTS['API'])
    page = await _read_in_turn(api.with_path(ROUTES['MODELS']).with_query({'q': model_id}), configuration)
    try:
        entries = CatalogPage.model_validate(page).models
    except ValidationError:
        raise KIEError(ErrorCode.TRANSPORT, MODEL_READ_UNREADABLE) from None
    entry = next((item for item in entries if item.model == model_id), None)
    if entry is None:
        raise KIEError(ErrorCode.INVALID_INPUT, MODEL_UNKNOWN.format(model=model_id, market=PAGES['MARKET']))
    document = await _read_in_turn(api.with_path(ROUTES['SCHEMA'].format(model=model_id)), configuration)
    return parse_model(entry, document)


def _delete_read(reads: dict[str, asyncio.Task[KIEModel]], model_id: str, read: asyncio.Task[KIEModel]) -> None:
    """Drop a finished read, so a later caller reads again when this one failed.

    Taking its failure here keeps a read whose callers all cancelled from failing unseen.
    """
    del reads[model_id]
    if not read.cancelled():
        read.exception()


async def _read_shared(model_id: str, configuration: Configuration) -> KIEModel:
    """Read one model, sharing the read with every caller that asks for it at the same time.

    A task belongs to its event loop, and ComfyUI may run each prompt on a new one, so the extension keeps the reads in
    flight per loop. A caller's cancel leaves the read running for the others.
    """
    reads = _READS.setdefault(asyncio.get_running_loop(), {})
    task = reads.get(model_id)
    if task is None:
        task = reads[model_id] = asyncio.create_task(_download_model(model_id, configuration))
        task.add_done_callback(lambda done: _delete_read(reads, model_id, done))
    return await asyncio.shield(task)


def _validate_kind(model: KIEModel, kind: Kind) -> None:
    """Refuse a model a paid node of this kind cannot run, naming the node that runs it."""
    if model.model_format is None:
        raise KIEError(ErrorCode.INVALID_INPUT, MODEL_OTHER_ROUTE.format(model=model.entry.model, route=model.route))
    if model.kind is None:
        raise KIEError(ErrorCode.INVALID_INPUT, MODEL_NO_KIND.format(model=model.entry.model))
    if model.kind != kind:
        names = {'made': KIND_NAMES[model.kind], 'node': KIND_NODES[model.kind], 'this': KIND_NODES[kind]}
        raise KIEError(ErrorCode.INVALID_INPUT, MODEL_KIND.format(model=model.entry.model, **names))


async def read_kie_model(model_id: str, kind: Kind | None, configuration: Configuration) -> KIEModel:
    """Read one model from KIE, refusing an ID that cannot be one, and one KIE does not know.

    A paid node passes its kind, and the read refuses a model of another kind too. Model: Info passes no kind.
    """
    example = DEFAULT_MODELS[kind or 'image']
    if not model_id:
        raise KIEError(ErrorCode.INVALID_INPUT, MODEL_EMPTY.format(example=example, market=PAGES['MARKET']))
    if not _MODEL_ID.match(model_id):
        raise KIEError(
            ErrorCode.INVALID_INPUT, MODEL_FORM.format(model=model_id, example=example, market=PAGES['MARKET'])
        )
    model = _MODELS.get(model_id) or await _read_shared(model_id, configuration)
    _MODELS[model_id] = model
    if kind is not None:
        _validate_kind(model, kind)
    return model


__all__ = ['read_kie_model']
