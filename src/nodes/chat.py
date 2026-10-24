"""Chat: Ask, which asks any KIE chat model one question, with images or documents when the model reads them."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast, override
from functools import partial

from comfy_api.latest import io
from comfy_execution.graph import ExecutionBlocker

from .base import PaidNode
from ..kie.chat import run_chat, parse_chat
from ..state.chat import Turn, ChatRequest, Conversation
from ..comfy.media import encode_local_file
from ..config.chat import EFFORTS
from ..state.files import KIEFile
from ..config.inputs import TOOLTIPS, RUN_NUMBER, INPUT_NAMES
from ..config.models import KIND_NODES, DEFAULT_MODELS
from ..comfy.execution import send_request
from ..config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES

if TYPE_CHECKING:
    import torch

    from ..state.chat import Document, ChatResult
    from ..state.models import KIEModel

# The text inputs, in node order: free text comes last.
_TEXTS = ('answer_schema', 'prompt', 'system_prompt', 'extra_fields')
# The effort that sends nothing.
_DEFAULT_EFFORT = EFFORTS[0]

# The sockets of the earlier turns and of everything the model reads besides the prompt.
_SOCKETS = (
    io.Custom(SOCKET_TYPES['CONVERSATION']).Input(
        'conversation', optional=True, tooltip='Connect a previous Chat: Ask to continue its conversation.'
    ),
    io.Custom(SOCKET_TYPES['DOCUMENTS']).Input(
        'documents',
        optional=True,
        tooltip='Connect Chat: Attach Document. PDFs need a GPT model; text files go to any model.',
    ),
    io.Image.Input(
        'images',
        optional=True,
        tooltip='Images for the model to read: one, a batch, or a list. Create List joins several Load Image nodes.',
    ),
)

# The text boxes, in the order of _TEXTS.
_TEXT_INPUTS = (
    io.String.Input(
        'answer_schema',
        default='',
        multiline=True,
        advanced=True,
        tooltip='A JSON schema the answer must follow, for GPT models; leave it empty for free text.',
    ),
    io.String.Input('prompt', default='', multiline=True, tooltip='The question or instruction.'),
    io.String.Input(
        'system_prompt',
        default='',
        multiline=True,
        optional=True,
        advanced=True,
        tooltip='Instructions the model follows for the whole answer.',
    ),
    io.String.Input(
        'extra_fields',
        default='',
        multiline=True,
        advanced=True,
        tooltip='A JSON object of request fields, added to the request as written. The node refuses a field it sets '
        'itself.',
    ),
)


def _build_outputs(result: ChatResult, history: Conversation, prompt: str) -> io.NodeOutput:
    """Return the answer and the reasoning, and extend the conversation with the words of this exchange."""
    turns = (*history.turns, Turn('user', prompt), Turn('assistant', result.text))
    reasoning: object = result.reasoning or ExecutionBlocker(None)
    return io.NodeOutput(result.text, reasoning, Conversation(turns))


class ChatAsk(PaidNode):
    """Send one chat request and return the answer, the reasoning, and the conversation."""

    kind = 'chat'
    list_inputs = frozenset({'images'})

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """List the model, the conversation, the documents, the images, the effort, the run number, and the text."""
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name=KIND_NODES['chat'],
            category=MENUS['CHAT'],
            description='Ask any KIE chat model, with images or documents when the model reads them.',
            inputs=[
                io.String.Input(INPUT_NAMES['MODEL'], default=DEFAULT_MODELS['chat'], tooltip=TOOLTIPS['MODEL']),
                *_SOCKETS,
                io.Combo.Input(
                    'reasoning_effort',
                    options=list(EFFORTS),
                    default=_DEFAULT_EFFORT,
                    advanced=True,
                    tooltip='How much the model thinks before answering. KIE takes it for GPT and Gemini models.',
                ),
                io.Int.Input(
                    INPUT_NAMES['RUN_NUMBER'],
                    default=RUN_NUMBER['DEFAULT'],
                    min=RUN_NUMBER['MIN'],
                    max=RUN_NUMBER['MAX'],
                    tooltip=TOOLTIPS['RUN_NUMBER'],
                ),
                *_TEXT_INPUTS,
            ],
            outputs=[
                io.String.Output('text', display_name='text'),
                io.String.Output('reasoning', display_name='reasoning'),
                io.Custom(SOCKET_TYPES['CONVERSATION']).Output('conversation', display_name='conversation'),
            ],
            is_input_list=True,
            hidden=[io.Hidden.unique_id],
        )

    @classmethod
    @override
    def check(cls, model: KIEModel, inputs: dict[str, object]) -> None:
        """Check the effort and the text boxes that the workflow sets, against the format of the model."""
        texts = {name: value if isinstance(value := inputs.get(name), str) else None for name in _TEXTS}
        effort = inputs.get('reasoning_effort')
        parse_chat(model, texts, effort if isinstance(effort, str) else None, ())

    @classmethod
    @override
    async def send(cls, node_id: str | None, **inputs: object) -> io.NodeOutput:
        """Ask the question once with the earlier turns, the documents, and every frame of every connected batch."""
        history = cast('Conversation | None', inputs.get('conversation')) or Conversation(())
        batches = cast('list[torch.Tensor] | None', inputs.get('images')) or []
        request = ChatRequest(
            model_id=str(inputs.get(INPUT_NAMES['MODEL']) or DEFAULT_MODELS['chat']).strip(),
            conversation=history,
            documents=cast('tuple[Document, ...] | None', inputs.get('documents')) or (),
            images=tuple(
                KIEFile(kind='image', url=None, media=frame, origin='local', field=None)
                for batch in batches
                for frame in batch
            ),
            reasoning_effort=str(inputs.get('reasoning_effort') or _DEFAULT_EFFORT),
            texts={name: str(inputs.get(name) or '') for name in _TEXTS},
        )
        run = partial(run_chat, request, encode_local_file)
        return await send_request(
            run, partial(_build_outputs, history=history, prompt=request.texts['prompt']), node_id
        )


__all__ = ['ChatAsk']
