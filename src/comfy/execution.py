"""Run requests to KIE with ComfyUI's progress bar, while ComfyUI's cancel stays live."""

from __future__ import annotations

from typing import TYPE_CHECKING
import asyncio
from functools import partial

from comfy_api.latest import ComfyAPI
from comfy.model_management import throw_exception_if_processing_interrupted

from .runtime import CONFIGURATION
from ..config.tasks import PROGRESS_STEPS
from ..config.execution import CANCELLATION_POLL_SECONDS

if TYPE_CHECKING:
    from typing import Any
    from collections.abc import Callable, Coroutine

    from comfy_api.latest import io

    from ..state.tasks import Progress
    from ..state.settings import Configuration


async def wait_for_request[T](task: asyncio.Task[T]) -> T:
    """Wait for the owned task that sends a request, and cancel it when ComfyUI's cancel arrives."""
    try:
        while not task.done():
            throw_exception_if_processing_interrupted()
            await asyncio.wait({task}, timeout=CANCELLATION_POLL_SECONDS)
        return await task
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)


async def wait_for_thread[T](work: Callable[[], T]) -> T:
    """Run blocking work in a thread, and let a cancel through only after the work ends."""
    task = asyncio.ensure_future(asyncio.to_thread(work))
    is_cancelled = False
    while not task.done():
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            is_cancelled = True
    if is_cancelled:
        raise asyncio.CancelledError
    return task.result()


async def send_request[Result](
    run: Callable[[Configuration, Progress], Coroutine[Any, Any, Result]],
    build_outputs: Callable[[Result], io.NodeOutput],
    node_id: str | None,
) -> io.NodeOutput:
    """Read the settings and key, send, and build the outputs of the node, with only the progress bar of ComfyUI.

    The bar belongs to the node: a node that another pack calls has no ID, so it leaves the bar of its caller alone.
    Building the outputs decodes media, which blocks, so it runs in a worker thread.
    """
    progress: Progress = None
    if node_id is not None:
        progress = partial(ComfyAPI().execution.set_progress, max_value=PROGRESS_STEPS['TOTAL'], node_id=node_id)
        await progress(0)
    configuration = await asyncio.to_thread(CONFIGURATION.read_configuration)
    result = await wait_for_request(asyncio.create_task(run(configuration, progress)))
    outputs = await wait_for_thread(lambda: build_outputs(result))
    if progress is not None:
        await progress(PROGRESS_STEPS['TOTAL'])
    return outputs


__all__ = ['send_request', 'wait_for_request', 'wait_for_thread']
