"""Turn one model's catalog entry and OpenAPI document into what the extension knows about the model.

Nothing here sends a request.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast
from urllib.parse import unquote

from ..state.errors import KIEError, ErrorCode
from ..state.models import KIEModel, ModelField
from ..config.models import JOB_ROUTE, KIND_ORDER, CHAT_FORMATS, MAX_REFERENCES, TASK_TYPE_KINDS
from ..config.messages.models import MODEL_NO_SCHEMA, MODEL_READ_UNREADABLE

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..state import Json
    from ..state.models import ModelFormat, CatalogEntry

# The schema keys that hold alternatives; a field of any one of them is a field of the model.
_BRANCH_KEYS = ('oneOf', 'anyOf', 'allOf')
# A field takes a link when the schema gives it this format, or its name ends like this.
_LINK_FORMAT = 'uri'
_LINK_ENDINGS = ('_url', '_urls')


def _find_component(reference: str, components: Mapping[str, Json]) -> Json:
    """Find the component a reference names; KIE escapes characters in its names, and some end in a space.

    Args:
        reference: The reference that names the component.
        components: The components by name.

    Returns:
        The component, or None when no name matches.

    """
    name = unquote(reference.rsplit('/', 1)[-1]).replace('~1', '/').replace('~0', '~')
    matches = (value for key, value in components.items() if key.strip() == name.strip())
    return next(matches, None)


def _follow_references(schema: Json, components: Mapping[str, Json]) -> dict[str, Json]:
    """Follow a schema's references to the schema itself; its own keys stay over the component's.

    Args:
        schema: The schema to follow. A value that is not an object counts as an empty schema.
        components: The components that the references point to.

    Returns:
        The schema with no reference left.

    Raises:
        KIEError: When the references go on past the limit of steps.

    """
    resolved = schema if isinstance(schema, dict) else {}
    for _ in range(MAX_REFERENCES):
        reference = resolved.get('$ref')
        if not isinstance(reference, str):
            return resolved
        target = _find_component(reference, components)
        own = {key: value for key, value in resolved.items() if key != '$ref'}
        resolved = {**(target if isinstance(target, dict) else {}), **own}
    raise KIEError(ErrorCode.TRANSPORT, MODEL_READ_UNREADABLE)


def _list_branches(schema: dict[str, Json], components: Mapping[str, Json]) -> list[dict[str, Json]]:
    """List the schema's alternatives, each resolved; a schema without any gives none.

    Args:
        schema: The schema whose alternatives are listed.
        components: The components that the references of each alternative name.

    Returns:
        The resolved alternatives.

    """
    branches: list[dict[str, Json]] = []
    for key in _BRANCH_KEYS:
        options = schema.get(key)
        if isinstance(options, list):
            branches.extend(_follow_references(option, components) for option in options)
    return branches


def _read_types(schema: dict[str, Json], components: Mapping[str, Json]) -> tuple[str, ...]:
    """Read a field's JSON types, from its type or from its alternatives, without null.

    Args:
        schema: The schema of the field.
        components: The components that the references of the alternatives name.

    Returns:
        The names of the JSON types, each one once.

    """
    declared = schema.get('type')
    if isinstance(declared, str):
        return (declared,)
    if isinstance(declared, list):
        return tuple(str(item) for item in declared if item != 'null')
    found = (_read_types(branch, components) for branch in _list_branches(schema, components))
    return tuple(dict.fromkeys(name for types in found for name in types if name != 'null'))


def _read_field(name: str, schema: dict[str, Json], *, required: bool, components: Mapping[str, Json]) -> ModelField:
    """Describe one input from its schema.

    Args:
        name: The name of the input.
        schema: The resolved schema of the input.
        required: Whether the model requires the input.
        components: The components that the references of the items and the alternatives name.

    Returns:
        The description of the input.

    """
    types = _read_types(schema, components)
    items = _follow_references(schema.get('items'), components)
    is_list = 'array' in types
    choices = schema.get('enum')
    max_items = schema.get('maxItems')
    max_length = schema.get('maxLength')
    bounds = {
        key: float(value)
        for key in ('minimum', 'maximum')
        if isinstance(value := schema.get(key), (int, float)) and not isinstance(value, bool)
    }
    return ModelField(
        name=name,
        schema_type=' | '.join(types) or 'any',
        required=required,
        default=schema.get('default'),
        choices=tuple(choice for choice in choices if choice is not None) if isinstance(choices, list) else (),
        minimum=bounds.get('minimum'),
        maximum=bounds.get('maximum'),
        is_list=is_list,
        max_items=max_items if isinstance(max_items, int) else None,
        max_length=max_length if isinstance(max_length, int) else None,
        takes_text='string' in types or (is_list and 'string' in _read_types(items, components)),
        is_link=_LINK_FORMAT in (schema.get('format'), items.get('format')) or name.endswith(_LINK_ENDINGS),
        description=' '.join(str(schema.get('description') or '').split()),
    )


def _read_fields(schema: dict[str, Json], components: Mapping[str, Json]) -> tuple[ModelField, ...]:
    """Describe every input of an object schema, its alternatives' inputs included.

    The model requires an input that every alternative requires. The order is the schema's own order of its fields.

    Args:
        schema: The object schema to read.
        components: The components that the references of each input name.

    Returns:
        The description of every input.

    """
    branches = _list_branches(schema, components)
    properties: dict[str, Json] = dict(cast('dict[str, Json]', schema.get('properties') or {}))
    for branch in branches:
        properties.update(
            {
                key: value
                for key, value in cast('dict[str, Json]', branch.get('properties') or {}).items()
                if key not in properties
            }
        )
    required = {str(name) for name in cast('list[Json]', schema.get('required') or [])}
    branch_required = [{str(name) for name in cast('list[Json]', branch.get('required') or [])} for branch in branches]
    if branch_required:
        required |= branch_required[0].intersection(*branch_required[1:])
    return tuple(
        _read_field(name, _follow_references(value, components), required=name in required, components=components)
        for name, value in properties.items()
    )


def _choose_format(route: str) -> ModelFormat | None:
    """Choose how the extension calls a model from its route; None for a route the extension does not use.

    Args:
        route: The route the model posts to.

    Returns:
        The name of the format, or None.

    """
    if route == JOB_ROUTE:
        return 'job'
    return next((cast('ModelFormat', name) for ending, name in CHAT_FORMATS.items() if route.endswith(ending)), None)


def parse_model(entry: CatalogEntry, document: Json) -> KIEModel:
    """Describe one model from its catalog entry and the schema reply that holds its OpenAPI document.

    A job model's inputs are the fields of its input object; a chat model's are its request's top-level fields.

    Args:
        entry: The catalog entry of the model.
        document: The schema reply for the model.

    Returns:
        The description of the model.

    Raises:
        KIEError: When the reply holds no OpenAPI document, or its references cannot be followed.

    """
    openapi = document.get('openapi') if isinstance(document, dict) else None
    if not isinstance(openapi, dict):
        raise KIEError(ErrorCode.INVALID_INPUT, MODEL_NO_SCHEMA.format(model=entry.model))
    components = cast('dict[str, Json]', _follow_references(openapi.get('components'), {}).get('schemas') or {})
    route, operation = _find_route(cast('dict[str, Json]', openapi.get('paths') or {}))
    body = _follow_references(_find_body(operation.get('post')), components)
    model_format = _choose_format(route)
    kinds = {TASK_TYPE_KINDS[task_type] for task_type in entry.task_types if task_type in TASK_TYPE_KINDS}
    target = (
        _follow_references(cast('dict[str, Json]', body.get('properties') or {}).get('input'), components)
        if model_format == 'job'
        else body
    )
    return KIEModel(
        entry=entry,
        kind=next((kind for kind in KIND_ORDER if kind in kinds), None),
        route=route,
        model_format=model_format,
        fields=_read_fields(target, components),
    )


def _find_route(paths: dict[str, Json]) -> tuple[str, dict[str, Json]]:
    """Find the route a model posts to, and its operations; a document without one gives an empty route.

    Args:
        paths: The paths of the OpenAPI document.

    Returns:
        The route, then its operations.

    """
    for path, item in paths.items():
        if isinstance(item, dict) and 'post' in item:
            return path, item
    return '', {}


def _find_body(operation: Json) -> Json:
    """Find the JSON schema of an operation's request body; None when it has none.

    Args:
        operation: The post operation of the route. A value that is not an object has no body.

    Returns:
        The schema of the JSON body, or None.

    """
    body = operation.get('requestBody') if isinstance(operation, dict) else None
    content = body.get('content') if isinstance(body, dict) else None
    media = content.get('application/json') if isinstance(content, dict) else None
    return media.get('schema') if isinstance(media, dict) else None


__all__ = ['parse_model']
