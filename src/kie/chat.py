"""Ask a KIE chat model one question in the model's own format, and read its answer and reasoning.

KIE serves chat models in four formats: OpenAI Responses, Anthropic Messages, Chat Completions, and native Gemini. Each
model's schema names its route, and the route names the format.
"""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING, cast
import asyncio
from dataclasses import dataclass

from yarl import URL
from pydantic import ValidationError

from .models import read_kie_model
from .arguments import parse_arguments_text
from .transport import send_chat
from ..config.kie import HOSTS
from ..state.chat import ChatResult, ChatReplyParts
from ..config.chat import ROLES, ANSWER_NAME, PDF_FORMATS, DOCUMENT_TEXT, FORMAT_EFFORTS, SCHEMA_FORMATS
from ..state.errors import KIEError, ErrorCode
from ..state.parsing import parse_fields
from ..config.messages.run import REPLY_UNREADABLE
from ..config.messages.chat import (
    PDF_REFUSED,
    PROMPT_EMPTY,
    EFFORT_REFUSED,
    SCHEMA_REFUSED,
    CHAT_FIELD_TWICE,
    CHAT_REPLY_EMPTY,
    EFFORT_NOT_TAKEN,
    ANSWER_SCHEMA_INVALID,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Callable, Sequence

    from ..state import Json
    from ..state.chat import Turn, Document, ChatRequest
    from ..state.files import KIEFile, EncodedFile
    from ..state.tasks import Progress
    from ..state.models import KIEModel
    from ..state.settings import Configuration

# The effort that sends nothing.
_DEFAULT_EFFORT = 'default'


@dataclass(frozen=True, slots=True)
class _Question:
    """Everything one request sends besides its options.

    Attributes:
        texts: The text boxes by input name.
        turns: The earlier turns, oldest first.
        documents: The attached documents; only a format in PDF_FORMATS receives a PDF.
        images: Each image as its content type and its bytes in base64.

    """

    texts: Mapping[str, str]
    turns: tuple[Turn, ...]
    documents: tuple[Document, ...]
    images: Sequence[tuple[str, str]]


def _build_responses(model: KIEModel, question: _Question, options: dict[str, Json]) -> dict[str, Json]:
    """Build an OpenAI Responses request: the system prompt, the earlier turns, then the question as input messages."""
    content: list[Json] = [
        {'type': 'input_file', 'filename': document.name, 'file_data': document.file_url}
        if document.file_url is not None
        else {'type': 'input_text', 'text': DOCUMENT_TEXT.format(name=document.name, text=document.text)}
        for document in question.documents
    ]
    content.extend(
        [{'type': 'input_image', 'image_url': f'data:{kind};base64,{data}'} for kind, data in question.images]
    )
    content.append({'type': 'input_text', 'text': question.texts['prompt']})
    messages: list[Json] = [
        {
            'role': turn.role,
            'content': [{'type': 'input_text' if turn.role == ROLES['USER'] else 'output_text', 'text': turn.text}],
        }
        for turn in question.turns
    ]
    messages.append({'role': ROLES['USER'], 'content': content})
    if question.texts['system_prompt'].strip():
        messages.insert(
            0, {'role': ROLES['SYSTEM'], 'content': [{'type': 'input_text', 'text': question.texts['system_prompt']}]}
        )
    body: dict[str, Json] = {'model': model.entry.model, 'stream': False, 'input': messages}
    if 'effort' in options:
        body['reasoning'] = {'effort': options['effort']}
    if 'schema' in options:
        body['text'] = {
            'format': {'type': 'json_schema', 'name': ANSWER_NAME, 'strict': True, 'schema': options['schema']}
        }
    return body


def _build_messages(model: KIEModel, question: _Question, _options: dict[str, Json]) -> dict[str, Json]:
    """Build an Anthropic Messages request: the system prompt apart, the earlier turns, then the question.

    KIE honors no effort, no answer schema, and no PDF for Claude, so the options are always empty here, and every
    document is text.
    """
    content: list[Json] = [
        {'type': 'text', 'text': DOCUMENT_TEXT.format(name=document.name, text=document.text)}
        for document in question.documents
    ]
    content.extend(
        [
            {'type': 'image', 'source': {'type': 'base64', 'media_type': kind, 'data': data}}
            for kind, data in question.images
        ]
    )
    content.append({'type': 'text', 'text': question.texts['prompt']})
    messages: list[Json] = [
        {'role': turn.role, 'content': [{'type': 'text', 'text': turn.text}]} for turn in question.turns
    ]
    messages.append({'role': ROLES['USER'], 'content': content})
    body: dict[str, Json] = {'model': model.entry.model, 'stream': False, 'messages': messages}
    if question.texts['system_prompt'].strip():
        body['system'] = question.texts['system_prompt']
    return body


def _build_completions(_model: KIEModel, question: _Question, options: dict[str, Json]) -> dict[str, Json]:
    """Build a Chat Completions request: every image as an image_url part, and every document as text."""
    content: list[Json] = [
        {'type': 'text', 'text': DOCUMENT_TEXT.format(name=document.name, text=document.text)}
        for document in question.documents
    ]
    content.extend(
        [{'type': 'image_url', 'image_url': {'url': f'data:{kind};base64,{data}'}} for kind, data in question.images]
    )
    content.append({'type': 'text', 'text': question.texts['prompt']})
    messages: list[Json] = [{'role': turn.role, 'content': turn.text} for turn in question.turns]
    messages.append({'role': ROLES['USER'], 'content': content})
    if question.texts['system_prompt'].strip():
        messages.insert(0, {'role': ROLES['SYSTEM'], 'content': question.texts['system_prompt']})
    body: dict[str, Json] = {'stream': False, 'messages': messages}
    if 'effort' in options:
        body['reasoning_effort'] = options['effort']
    if 'schema' in options:
        body['response_format'] = {
            'type': 'json_schema',
            'json_schema': {'name': ANSWER_NAME, 'strict': True, 'schema': options['schema']},
        }
    return body


def _build_gemini(_model: KIEModel, question: _Question, options: dict[str, Json]) -> dict[str, Json]:
    """Build a native Gemini request: images as inline data, and the system prompt as a system instruction.

    The route names the model, so the body does not. Gemini names the earlier answers of the model by the role model.
    """
    parts: list[Json] = [
        {'text': DOCUMENT_TEXT.format(name=document.name, text=document.text)} for document in question.documents
    ]
    parts.extend([{'inline_data': {'mime_type': kind, 'data': data}} for kind, data in question.images])
    parts.append({'text': question.texts['prompt']})
    contents: list[Json] = [
        {
            'role': ROLES['USER'] if turn.role == ROLES['USER'] else ROLES['GEMINI_ASSISTANT'],
            'parts': [{'text': turn.text}],
        }
        for turn in question.turns
    ]
    contents.append({'role': ROLES['USER'], 'parts': parts})
    body: dict[str, Json] = {'stream': False, 'contents': contents}
    if question.texts['system_prompt'].strip():
        body['systemInstruction'] = {'parts': [{'text': question.texts['system_prompt']}]}
    if 'effort' in options:
        body['generationConfig'] = {'thinkingConfig': {'thinkingLevel': options['effort']}}
    return body


_BUILDERS = {
    'responses': _build_responses,
    'messages': _build_messages,
    'completions': _build_completions,
    'gemini': _build_gemini,
}


def _read_reply(model_format: str, reply: Json) -> tuple[str, str]:
    """Read the answer and the shown reasoning from a reply in its format."""
    try:
        parts = ChatReplyParts.model_validate(reply)
    except ValidationError:
        raise KIEError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
    if model_format == 'responses':
        answer = [part.text for item in parts.output if item.type == 'message' for part in item.content]
        shown = [part.text for item in parts.output if item.type == 'reasoning' for part in item.summary]
    elif model_format == 'messages':
        answer = [part.text for part in parts.content if part.type == 'text']
        shown = [part.thinking for part in parts.content]
    elif model_format == 'completions':
        answer = [choice.message.content for choice in parts.choices]
        shown = [choice.message.reasoning_content for choice in parts.choices]
    else:
        gemini = [part for candidate in parts.candidates for part in candidate.content.parts]
        answer = [part.text for part in gemini if not part.thought]
        shown = [part.text for part in gemini if part.thought]
    return ''.join(text for text in answer if text), ''.join(text for text in shown if text)


def _read_options(model: KIEModel, effort: str | None, answer_schema: str | None) -> dict[str, Json]:
    """Check the effort and the answer schema against what KIE honors for the format, and return the ones set."""
    model_format = cast('str', model.model_format)
    options: dict[str, Json] = {}
    if effort is not None and effort != _DEFAULT_EFFORT:
        efforts = FORMAT_EFFORTS[model_format]
        if effort not in efforts:
            names = {'model': model.entry.model, 'efforts': ', '.join(efforts)}
            raise KIEError(ErrorCode.INVALID_INPUT, (EFFORT_REFUSED if efforts else EFFORT_NOT_TAKEN).format(**names))
        options['effort'] = effort
    if answer_schema is not None and answer_schema.strip():
        if model_format not in SCHEMA_FORMATS:
            raise KIEError(ErrorCode.INVALID_INPUT, SCHEMA_REFUSED.format(model=model.entry.model))
        try:
            options['schema'] = parse_fields(answer_schema)
        except KIEError:
            raise KIEError(ErrorCode.INVALID_INPUT, ANSWER_SCHEMA_INVALID.format()) from None
    return options


def parse_chat(
    model: KIEModel, texts: Mapping[str, str | None], effort: str | None, documents: Sequence[Document]
) -> tuple[dict[str, Json], dict[str, Json]]:
    """Make the checks that need no images: the prompt, the effort, the answer schema, the documents, and extra_fields.

    A None text or effort is an input fed by a link, known only when the node runs, so its checks wait until then.
    Returns the options of the format and the extra fields.
    """
    prompt = texts['prompt']
    if prompt is not None and not prompt.strip():
        raise KIEError(ErrorCode.INVALID_INPUT, PROMPT_EMPTY)
    model_format = cast('str', model.model_format)
    if model_format not in PDF_FORMATS and any(document.file_url is not None for document in documents):
        raise KIEError(ErrorCode.INVALID_INPUT, PDF_REFUSED.format(model=model.entry.model))
    options = _read_options(model, effort, texts['answer_schema'])
    extra_fields = parse_arguments_text(texts['extra_fields']) if texts['extra_fields'] is not None else {}
    # The node sets the same fields whatever the turns, documents, and images; a box fed by a link counts as empty.
    question = _Question({name: text or '' for name, text in texts.items()}, (), (), ())
    fields = _BUILDERS[model_format](model, question, options)
    twice = next((name for name in extra_fields if name in fields), None)
    if twice is not None:
        raise KIEError(ErrorCode.INVALID_INPUT, CHAT_FIELD_TWICE.format(field=twice, model=model.entry.model))
    return options, extra_fields


async def run_chat(
    request: ChatRequest, encode: Callable[[KIEFile], EncodedFile], configuration: Configuration, _progress: Progress
) -> ChatResult:
    """Read the model, make the free checks, encode the images, send the request once, and read the answer."""
    model = await read_kie_model(request.model_id, 'chat', configuration)
    options, extra_fields = parse_chat(model, request.texts, request.reasoning_effort, request.documents)
    encoded = [await asyncio.to_thread(encode, image) for image in request.images]
    images = [(file.content_type, base64.b64encode(file.content).decode()) for file in encoded]
    question = _Question(request.texts, request.conversation.turns, request.documents, images)
    body = _BUILDERS[cast('str', model.model_format)](model, question, options) | extra_fields
    reply = await send_chat(URL.build(scheme='https', host=HOSTS['API'], path=model.route), body, configuration)
    text, reasoning = _read_reply(cast('str', model.model_format), reply)
    if not text:
        raise KIEError(ErrorCode.UNAVAILABLE, CHAT_REPLY_EMPTY.format(model=model.entry.model))
    return ChatResult(text=text, reasoning=reasoning)


__all__ = ['parse_chat', 'run_chat']
