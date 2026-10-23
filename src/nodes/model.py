"""Report what any KIE model takes, read live from KIE."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, override
import asyncio

from comfy_api.latest import io

from ..kie.models import read_kie_model
from ..comfy.runtime import CONFIGURATION
from ..config.inputs import TOOLTIPS, INPUT_NAMES
from ..config.models import KIND_NODES, DEFAULT_MODELS
from ..comfy.execution import wait_for_request
from ..config.namespace import MENUS, NODE_PREFIX

if TYPE_CHECKING:
    from ..state import Json


def _format_bound(value: float | None) -> Json:
    """Show a whole-number bound without a decimal point, as the schema writes it."""
    if value is None:
        return None
    return int(value) if value.is_integer() else value


async def _read_report(model_id: str) -> io.NodeOutput:
    """Read one model from KIE with the saved key, and report it."""
    configuration = await asyncio.to_thread(CONFIGURATION.read_configuration)
    model = await read_kie_model(model_id, None, configuration)
    # Every key is present, with null where KIE gives no value; the input keys match the arguments of a paid node.
    inputs: list[Json] = [
        {
            'field': field.name,
            'type': field.schema_type,
            'required': field.required,
            'default': field.default,
            'choices': list(field.choices) or None,
            'minimum': _format_bound(field.minimum),
            'maximum': _format_bound(field.maximum),
            'list': field.is_list,
            'max_items': field.max_items,
            'max_length': field.max_length,
            'link': field.is_link,
            'description': field.description or None,
        }
        for field in model.fields
    ]
    report: dict[str, Json] = {
        'model': model.entry.model,
        'title': model.entry.title or None,
        'provider': model.entry.provider or None,
        'task_types': list(model.entry.task_types),
        'kind': model.kind,
        'node': KIND_NODES[model.kind] if model.kind is not None and model.model_format is not None else None,
        'format': model.model_format,
        'route': model.route or None,
        'inputs': inputs,
    }
    return io.NodeOutput(json.dumps(report, ensure_ascii=False))


class ModelInfo(io.ComfyNode):
    """Report any KIE model's inputs; the read is free, and needs the API key."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """List the model ID and the JSON the node returns."""
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='Model: Info',
            category=MENUS['SHARED'],
            description='Show the inputs any KIE model takes, as JSON. Free, and needs your KIE API key.',
            inputs=[io.String.Input(INPUT_NAMES['MODEL'], default=DEFAULT_MODELS['image'], tooltip=TOOLTIPS['MODEL'])],
            outputs=[io.String.Output('info', display_name='info')],
        )

    @classmethod
    @override
    async def execute(cls, *, model: str) -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] # reason: ComfyUI calls execute with the inputs the schema declares.
        """Read the model in an owned task, so ComfyUI's cancel stops the read."""
        return await wait_for_request(asyncio.create_task(_read_report(model.strip())))


__all__ = ['ModelInfo']
