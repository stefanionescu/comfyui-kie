"""Build the input of a task from the text boxes, named inputs, arguments, and files of a node, and refuse mistakes.

Every refusal comes before the node uploads or pays for anything. KIE checks values itself, free, when it creates the
task, so values stay KIE's to check. KIE ignores an input a model does not take and still bills the task, so the
extension refuses an unknown input name.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..state.errors import KIEError, ErrorCode
from ..state.parsing import parse_json
from ..config.messages.inputs import (
    FIELD_TWICE,
    JSON_SHAPES,
    TEXT_UNUSED,
    FIELD_NOT_FILE,
    FIELD_ONE_FILE,
    FIELD_REQUIRED,
    FIELD_TOO_MANY,
    TEXT_NOT_TAKEN,
    ARGUMENTS_SHAPE,
    SETTING_UNKNOWN,
    ARGUMENT_UNKNOWN,
    ARGUMENTS_INVALID,
    FILE_FIELD_MISSING,
    FILE_FIELD_UNKNOWN,
)
from ..config.messages.requests import JSON_SYNTAX

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ..state import Json
    from ..state.files import KIEFile, FieldValue
    from ..state.models import KIEModel, ModelField

# How a refusal names a JSON value by its Python type; bool comes before int, which it subclasses.
_SHAPES: tuple[tuple[type, str], ...] = ((bool, 'boolean'), (list, 'array'), (str, 'string'), (int, 'number'))
# The name File: Add goes by when a refusal says what sets an input.
_FILE_SOURCE = 'File: Add'


def _parse_arguments_text(text: str) -> dict[str, Json]:
    """Read the arguments box as one JSON object; empty text is an empty object."""
    if not text.strip():
        return {}
    try:
        value = parse_json(text)
    except KIEError as error:
        if str(error) != JSON_SYNTAX:
            raise
        raise KIEError(ErrorCode.INVALID_INPUT, ARGUMENTS_INVALID.format()) from None
    if not isinstance(value, dict):
        shape = next(
            (name for kind, name in _SHAPES if isinstance(value, kind)), 'number' if value is not None else 'null'
        )
        raise KIEError(ErrorCode.INVALID_INPUT, ARGUMENTS_SHAPE.format(shape=JSON_SHAPES[shape]))
    return value


def _add_text(model: KIEModel, name: str, text: str, values: dict[str, Json]) -> None:
    """Add one text box under its own name, refusing a box the model has no input for, or that arguments sets too."""
    model_id = model.entry.model
    if name in values:
        raise KIEError(ErrorCode.INVALID_INPUT, FIELD_TWICE.format(field=name, source=f'the {name} input'))
    if not any(field.name == name for field in model.fields):
        texts = [field.name for field in model.fields if field.schema_type == 'string']
        message = TEXT_UNUSED.format(model=model_id, field=name, fields=', '.join(texts)) if texts else None
        raise KIEError(ErrorCode.INVALID_INPUT, message or TEXT_NOT_TAKEN.format(model=model_id, field=name))
    values[name] = text


def _add_setting(field: ModelField | None, name: str, value: Json, values: dict[str, Json], model_id: str) -> None:
    """Add one named input under its own name, as the type the model's input takes.

    A number goes as text to an input that takes only text, such as a duration that KIE lists as the text 5.
    """
    if field is None:
        raise KIEError(ErrorCode.INVALID_INPUT, SETTING_UNKNOWN.format(model=model_id, field=name))
    if name in values:
        raise KIEError(ErrorCode.INVALID_INPUT, FIELD_TWICE.format(field=name, source=f'the {name} input'))
    types = set(field.schema_type.split(' | '))
    is_text_only = 'string' in types and not types & {'integer', 'number'}
    values[name] = str(value) if is_text_only and isinstance(value, int) and not isinstance(value, bool) else value


def parse_input(
    model: KIEModel, texts: Mapping[str, str | None], settings: Mapping[str, Json], arguments: str | None
) -> dict[str, Json]:
    """Make the checks that need no files: the arguments, their input names, the text boxes, and the named inputs.

    A None text or arguments is an input fed by a link, known only when the node runs, so its checks wait until then.
    Returns the arguments first, then the text boxes and the named inputs.
    """
    values = _parse_arguments_text(arguments) if arguments is not None else {}
    fields = {field.name: field for field in model.fields}
    unknown = next((name for name in values if name not in fields), None)
    if unknown is not None:
        raise KIEError(ErrorCode.INVALID_INPUT, ARGUMENT_UNKNOWN.format(model=model.entry.model, field=unknown))
    for name, text in texts.items():
        if text is not None and text.strip():
            _add_text(model, name, text, values)
    for name, value in settings.items():
        _add_setting(fields.get(name), name, value, values, model.entry.model)
    return values


def _group_files(model: KIEModel, files: Sequence[KIEFile], values: Mapping[str, Json]) -> dict[str, list[KIEFile]]:
    """Group File: Add's files by the input each names, in the order they came, checking each input."""
    fields = {field.name: field for field in model.fields}
    groups: dict[str, list[KIEFile]] = {}
    for file in files:
        if file.field is None:
            raise KIEError(ErrorCode.INVALID_INPUT, FILE_FIELD_MISSING)
        names = {'model': model.entry.model, 'field': file.field}
        field = fields.get(file.field)
        if field is None:
            raise KIEError(ErrorCode.INVALID_INPUT, FILE_FIELD_UNKNOWN.format(**names))
        if not field.takes_text:
            raise KIEError(ErrorCode.INVALID_INPUT, FIELD_NOT_FILE.format(**names))
        if field.name in values:
            raise KIEError(ErrorCode.INVALID_INPUT, FIELD_TWICE.format(field=field.name, source=_FILE_SOURCE))
        groups.setdefault(field.name, []).append(file)
    return groups


def _validate_count(model: KIEModel, field: ModelField, count: int) -> None:
    """Refuse more than one file on an input that takes one, and more files than a list input takes."""
    maximum = field.max_items
    if not field.is_list and count > 1:
        raise KIEError(ErrorCode.INVALID_INPUT, FIELD_ONE_FILE.format(field=field.name, count=count))
    if maximum is not None and count > maximum:
        names = {'field': field.name, 'model': model.entry.model, 'maximum': maximum, 'count': count}
        raise KIEError(ErrorCode.INVALID_INPUT, FIELD_TOO_MANY.format(**names, extra=count - maximum))


def build_input(
    model: KIEModel,
    texts: Mapping[str, str],
    settings: Mapping[str, Json],
    arguments: str,
    files: Sequence[KIEFile],
) -> dict[str, FieldValue]:
    """Build the input of the task by KIE input name, and refuse the first problem before the node uploads or pays.

    A list input always gets a list of files, even with one file, as KIE's schema shapes it. A required input that
    nothing sets takes the default that the schema of the model gives it; without one, the node refuses the task.
    """
    values = parse_input(model, texts, settings, arguments)
    groups = _group_files(model, files, values)
    fields = {field.name: field for field in model.fields}
    built: dict[str, FieldValue] = dict(values)
    for name, items in groups.items():
        _validate_count(model, fields[name], len(items))
        built[name] = tuple(items) if fields[name].is_list else items[0]
    for field in model.fields:
        if field.required and field.name not in built:
            if field.default is None:
                raise KIEError(
                    ErrorCode.INVALID_INPUT, FIELD_REQUIRED.format(field=field.name, model=model.entry.model)
                )
            built[field.name] = field.default
    return built


__all__ = ['build_input', 'parse_input']
