"""Parse JSON within size and depth limits, and refuse duplicate keys and values that JSON cannot hold."""

import json
import math
from typing import cast

from . import Json
from .errors import KIEError, ErrorCode
from ..config.security import JSON_LIMITS
from ..config.messages.requests import JSON_SIZE, JSON_DEPTH, JSON_SYNTAX, JSON_VALUES, JSON_MAPPING, JSON_DUPLICATE_KEY


def _build_fields(pairs: list[tuple[str, Json]]) -> dict[str, Json]:
    """Build a JSON object, and refuse a key that appears twice.

    Args:
        pairs: The keys and values of one JSON object, in the order they were read.

    Returns:
        The object with every key once.

    Raises:
        ValueError: When a key appears twice.

    """
    result: dict[str, Json] = {}
    for key, value in pairs:
        if key in result:
            message = JSON_DUPLICATE_KEY
            raise ValueError(message)
        result[key] = value
    return result


def _validate_json(value: object, *, max_depth: int = JSON_LIMITS['MAX_DEPTH']) -> Json:
    """Copy JSON values within the nesting limit, and refuse other Python objects.

    Args:
        value: The parsed value to check.
        max_depth: The count of nesting levels that are still allowed below this value.

    Returns:
        The checked copy of the value.

    Raises:
        KIEError: When the value is nested too deep or holds something JSON cannot hold.

    """
    if max_depth < 0:
        raise KIEError(ErrorCode.INVALID_INPUT, JSON_DEPTH)
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    if isinstance(value, list):
        items = cast('list[object]', value)
        return [_validate_json(item, max_depth=max_depth - 1) for item in items]
    if isinstance(value, dict):
        entries = cast('dict[object, object]', value)
        if all(isinstance(key, str) for key in entries):
            return {cast('str', key): _validate_json(item, max_depth=max_depth - 1) for key, item in entries.items()}
    raise KIEError(ErrorCode.INVALID_INPUT, JSON_VALUES)


def parse_json(text: str, *, max_bytes: int = JSON_LIMITS['MAX_BYTES']) -> Json:
    """Refuse JSON that is too large, too deep, has a repeated key, or holds a value that is not finite.

    Args:
        text: The JSON text to parse.
        max_bytes: The largest size of the text that is accepted, in UTF-8 bytes.

    Returns:
        The parsed JSON value.

    Raises:
        KIEError: When the text is too large, is not valid JSON, or breaks one of the limits.

    """
    if len(text.encode('utf-8')) > max_bytes:
        raise KIEError(ErrorCode.INVALID_INPUT, JSON_SIZE)
    try:
        value = cast('object', json.loads(text, object_pairs_hook=_build_fields))
        return _validate_json(value)
    except (ValueError, RecursionError) as error:
        raise KIEError(ErrorCode.INVALID_INPUT, JSON_SYNTAX) from error


def parse_fields(text: str, *, max_bytes: int = JSON_LIMITS['MAX_BYTES']) -> dict[str, Json]:
    """Parse JSON as parse_json does, and refuse anything but an object.

    Args:
        text: The JSON text of one object.
        max_bytes: The size limit in bytes that parse_json applies to the text.

    Returns:
        The parsed JSON object.

    Raises:
        KIEError: When the text fails the checks of parse_json or is not an object.

    """
    value = parse_json(text, max_bytes=max_bytes)
    if not isinstance(value, dict):
        raise KIEError(ErrorCode.INVALID_INPUT, JSON_MAPPING)
    return value


__all__ = ['parse_fields', 'parse_json']
