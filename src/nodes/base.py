"""The cache key, the run number, the free checks, and the list inputs every paid node shares."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, cast, override
import asyncio

from comfy_api.latest import io

from ..kie.models import read_kie_model
from ..state.errors import KIEError, ErrorCode
from ..comfy.runtime import CONFIGURATION
from ..config.inputs import INPUT_NAMES
from ..config.messages.inputs import SINGLE_VALUE

if TYPE_CHECKING:
    from collections.abc import Callable, Awaitable

    from ..state.models import Kind, KIEModel


class PaidNode(io.ComfyNode):
    """A node that sends a billed request, with the cache key, checks, and run-number input every paid node shares.

    Attributes:
        kind: What the models of the node make; the node refuses a model of another kind before paying.
        list_inputs: The inputs of a node that takes input lists which may hold several items; every other input
            reaches check and send as its one value.
        check: The free checks of the node against its model, which raise KIEError. A value fed by a link is missing
            until the workflow runs, and the node checks it then.
        send: The typed entry point of the node, which receives the ID of the node, or None for a direct call, and every
            saved input except the run number.

    """

    kind: ClassVar[Kind]
    list_inputs: ClassVar[frozenset[str]] = frozenset()
    check: ClassVar[Callable[[KIEModel, dict[str, object]], None]]
    send: ClassVar[Callable[..., Awaitable[io.NodeOutput]]]

    @classmethod
    @override
    async def fingerprint_inputs(cls, **_inputs: object) -> str:
        """Add the API key's token to the cache key, so a new key runs the node again."""
        configuration = await asyncio.to_thread(CONFIGURATION.read_configuration)
        return configuration.generation

    @classmethod
    @override
    async def validate_inputs(cls, **inputs: object) -> bool | str:  # pyright: ignore[reportIncompatibleMethodOverride] # reason: ComfyUI passes every input by name, the dynamic settings included.
        """Read the model and make the free checks when ComfyUI queues the workflow, before any node runs, and bills.

        ComfyUI hands a validator every dynamic setting, whatever inputs it names, so this one takes every input.
        ComfyUI then skips its own range and choice checks, and KIE checks each value itself, free.
        """
        try:
            values = cls.read_values(inputs)
            model = values.get(INPUT_NAMES['MODEL'])
            if isinstance(model, str):
                configuration = await asyncio.to_thread(CONFIGURATION.read_configuration)
                cls.check(await read_kie_model(model.strip(), cls.kind, configuration), values)
        except KIEError as error:
            return str(error)
        return True

    @classmethod
    @override
    async def execute(cls, **inputs: object) -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] # reason: ComfyUI awaits an async execute with the inputs the schema declares.
        """Drop the run number, which only defeats ComfyUI's cache, and send.

        ComfyUI sets hidden on the class it runs. A pack that calls the node directly sets an empty hidden, so that call
        has no node ID and no progress bar.
        """
        inputs.pop(INPUT_NAMES['RUN_NUMBER'], None)
        node_id = cls.hidden.unique_id
        return await cls.send(node_id, **cls.read_values(inputs))

    @classmethod
    def read_values(cls, inputs: dict[str, object]) -> dict[str, object]:
        """Take the one value of each input that holds one; a node with input lists receives every input as a list."""
        if not cls.list_inputs:
            return inputs
        values: dict[str, object] = {}
        for name, value in inputs.items():
            items = cast('list[object]', value)
            if name not in cls.list_inputs and len(items) != 1:
                raise KIEError(ErrorCode.INVALID_INPUT, SINGLE_VALUE.format(name=name))
            values[name] = items if name in cls.list_inputs else items[0]
        return values


__all__ = ['PaidNode']
