"""Wait for requests to KIE while ComfyUI's cancel stays live."""

from __future__ import annotations

import asyncio

from comfy.model_management import throw_exception_if_processing_interrupted

from ..config.execution import CANCELLATION_POLL_SECONDS


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


__all__ = ['wait_for_request']
