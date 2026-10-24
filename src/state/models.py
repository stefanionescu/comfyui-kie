"""What the extension knows about one KIE model: where it runs, what it makes, and the inputs it takes."""

from typing import Literal
from dataclasses import dataclass

from pydantic import Field, BaseModel, ConfigDict

from . import Json, Reply

# What a model makes: one paid node for each kind.
type Kind = Literal['image', 'video', 'audio', 'chat']
# How the extension calls a model: as a job through KIE's task API, or in one of KIE's four chat formats.
type ModelFormat = Literal['job', 'responses', 'messages', 'completions', 'gemini']


@dataclass(frozen=True, slots=True)
class ModelField:
    """One input of a model, as its schema describes it.

    Attributes:
        name: The field's exact name, which arguments and File: Add use.
        schema_type: The JSON type as the schema writes it, with the types of a union joined by a vertical bar.
        required: Whether the model refuses a request without it.
        default: The value the model uses when the request leaves the field out, or None.
        choices: The values the field takes, or none when the schema lists none.
        minimum: The smallest number the field takes, or None.
        maximum: The largest number the field takes, or None.
        is_list: Whether the field takes a list.
        max_items: The most items a list field takes, or None.
        max_length: The longest text the field takes, in characters, or None.
        takes_text: Whether the field takes text or a list of text, as a file link needs.
        is_link: Whether the schema marks the field as a link: its format is uri, or its name ends in _url or _urls.
        description: The schema's description, with its whitespace collapsed.

    """

    name: str
    schema_type: str
    required: bool
    default: Json
    choices: tuple[Json, ...]
    minimum: float | None
    maximum: float | None
    is_list: bool
    max_items: int | None
    max_length: int | None
    takes_text: bool
    is_link: bool
    description: str


class Envelope(Reply):
    """KIE's reply around every result: a code, a message, and the result itself.

    Attributes:
        code: 200 for success; KIE's error code otherwise.
        msg: KIE's message, or None.
        payload: The result, which KIE names data.

    """

    code: int
    msg: str | None = None
    payload: Json = Field(default=None, alias='data')


class ChatError(Reply):
    """The error object of a failed Claude reply.

    Attributes:
        message: The reason.

    """

    message: str | None = None


class ChatReply(BaseModel):
    """A chat reply: the model's own document, or KIE's envelope with an error code, or a Claude error object.

    It keeps every field, because the reply goes to the result output whole.

    Attributes:
        code: KIE's error code, when KIE wrapped the reply.
        msg: KIE's message, when KIE wrapped the reply.
        error: Claude's error object, when Claude refused.

    """

    model_config = ConfigDict(extra='allow', frozen=True)

    code: int | None = None
    msg: str | None = None
    error: ChatError | None = None


class CatalogEntry(Reply):
    """One model in KIE's catalog.

    Attributes:
        model: The model's ID.
        title: Its title.
        provider: Its maker.
        task_types: What it does, such as Text to Image; KIE names this taskType.

    """

    model: str
    title: str = ''
    provider: str = ''
    task_types: tuple[str, ...] = Field(default=(), alias='taskType')


class CatalogPage(Reply):
    """The models a catalog search found.

    Attributes:
        models: The models, in KIE's order.

    """

    models: tuple[CatalogEntry, ...] = ()


@dataclass(frozen=True, slots=True)
class KIEModel:
    """One KIE model: its catalog entry, and the inputs its schema describes.

    Attributes:
        entry: The model's catalog entry: its ID, title, maker, and task types.
        kind: What the model makes, or None when its task types name no kind.
        route: The route that runs the model.
        model_format: job, or the chat format of a chat model, or None for a route the extension does not use.
        fields: The model's inputs: the job's input fields, or the chat request's top-level fields.

    """

    entry: CatalogEntry
    kind: Kind | None
    route: str
    model_format: ModelFormat | None
    fields: tuple[ModelField, ...]


# Other modules import the type aliases by name; __all__ lists the runtime names.
__all__ = ['CatalogEntry', 'CatalogPage', 'ChatError', 'ChatReply', 'Envelope', 'KIEModel', 'ModelField']
