"""One chat request that Chat: Ask makes, and what the model answered."""

from typing import Literal
from dataclasses import dataclass

from . import Reply
from .files import KIEFile


@dataclass(frozen=True, slots=True)
class Document:
    """One file attached to a chat request.

    Attributes:
        name: The name of the file, which the request carries.
        media_type: The media type of the file.
        text: The contents of a text file.
        file_url: A PDF as a data URL.

    """

    name: str
    media_type: str
    text: str | None
    file_url: str | None


@dataclass(frozen=True, slots=True)
class Turn:
    """One message of an earlier exchange.

    Attributes:
        role: Who wrote the message.
        text: What the message says.

    """

    role: Literal['user', 'assistant']
    text: str


@dataclass(frozen=True, slots=True)
class Conversation:
    """The turns before the next question, oldest first.

    Attributes:
        turns: The earlier messages.

    """

    turns: tuple[Turn, ...]


@dataclass(frozen=True, slots=True)
class ChatRequest:
    """One question to a chat model, as the inputs of Chat: Ask came.

    Attributes:
        model_id: The model ID as typed, stripped.
        conversation: The earlier turns, oldest first.
        documents: The attached documents, in the order of the chain.
        images: The connected images, one file for each frame.
        reasoning_effort: The chosen effort, or default.
        texts: The text boxes by input name: json_schema, prompt, system_prompt, and extra_fields.

    """

    model_id: str
    conversation: Conversation
    documents: tuple[Document, ...]
    images: tuple[KIEFile, ...]
    reasoning_effort: str
    texts: dict[str, str]


@dataclass(frozen=True, slots=True)
class ChatResult:
    """What a chat model answered.

    Attributes:
        text: The answer.
        reasoning: The reasoning the model showed, or empty text.

    """

    text: str
    reasoning: str


class TextPart(Reply):
    """One part of a reply that may hold text or reasoning.

    Attributes:
        type: The kind of part, where the format names one.
        text: The text, or None.
        thinking: Claude's reasoning, or None.
        thought: Whether a Gemini part holds reasoning.

    """

    type: str | None = None
    text: str | None = None
    thinking: str | None = None
    thought: bool = False


class ResponsesItem(Reply):
    """One item of an OpenAI Responses reply: a message, or the reasoning.

    Attributes:
        type: message or reasoning.
        content: The parts of a message.
        summary: The parts of the reasoning.

    """

    type: str | None = None
    content: tuple[TextPart, ...] = ()
    summary: tuple[TextPart, ...] = ()


class CompletionsMessage(Reply):
    """The message of one Chat Completions choice.

    Attributes:
        content: The answer.
        reasoning_content: The reasoning, where the model shows it.

    """

    content: str | None = None
    reasoning_content: str | None = None


class CompletionsChoice(Reply):
    """One Chat Completions choice.

    Attributes:
        message: Its message.

    """

    message: CompletionsMessage = CompletionsMessage()


class GeminiContent(Reply):
    """The content of one Gemini candidate.

    Attributes:
        parts: The answer parts and the reasoning parts together.

    """

    parts: tuple[TextPart, ...] = ()


class GeminiCandidate(Reply):
    """One Gemini candidate.

    Attributes:
        content: Its content.

    """

    content: GeminiContent = GeminiContent()


class ChatReplyParts(Reply):
    """The parts of a chat reply that hold text, in whichever format the reply came.

    Attributes:
        output: The items of an OpenAI Responses reply.
        content: The parts of a Claude reply.
        choices: The choices of a Chat Completions reply.
        candidates: The candidates of a Gemini reply.

    """

    output: tuple[ResponsesItem, ...] = ()
    content: tuple[TextPart, ...] = ()
    choices: tuple[CompletionsChoice, ...] = ()
    candidates: tuple[GeminiCandidate, ...] = ()


__all__ = [
    'ChatReplyParts',
    'ChatRequest',
    'ChatResult',
    'CompletionsChoice',
    'CompletionsMessage',
    'Conversation',
    'Document',
    'GeminiCandidate',
    'GeminiContent',
    'ResponsesItem',
    'TextPart',
    'Turn',
]
