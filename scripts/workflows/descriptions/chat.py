"""The chat workflows: write a product listing as JSON, and write a host script in a conversation."""

import json

from scripts.nodes.host import HostNode
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.page.config import STAGE_COLOUR, TEXT_PREVIEW
from scripts.workflows.descriptions.nodes import CHAT_ASK, ATTACH_DOCUMENT
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.descriptions.texts import SHARED_TEXTS

GPT_LUNA = 'gpt-6-luna'
GEMINI_FLASH = 'gemini-3-8-flash'
LISTING_SCHEMA = json.dumps(
    {
        'name': 'listing',
        'strict': True,
        'schema': {
            'type': 'object',
            'properties': {
                'title': {'type': 'string'},
                'bullets': {'type': 'array', 'items': {'type': 'string'}},
                'price': {'type': 'string'},
            },
            'required': ['title', 'bullets', 'price'],
            'additionalProperties': False,
        },
    },
    indent=2,
)
LISTING_TEXTS = WORKFLOW_TEXTS['chat-01-write-a-product-listing']
SCRIPT_TEXTS = WORKFLOW_TEXTS['chat-02-write-a-host-script']

LISTING = Subgraph(
    name=SHARED_TEXTS['listing'],
    nodes=(
        Node(
            'list',
            CHAT_ASK,
            {
                'model': GPT_LUNA,
                'json_schema': LISTING_SCHEMA,
                'prompt': (
                    'Write a marketplace listing for this product: a title, three to five bullets, and the price. Use '
                    'only facts from the photo and the spec.'
                ),
            },
            is_paid=True,
        ),
        Node('save', HostNode.SAVE_TEXT, {'filename_prefix': 'text/kie/listing', 'format': 'json'}),
    ),
    links=(('list.text', 'save.text'),),
    columns=(('list',), ('save',)),
    inputs=(('images', 'list.images'), ('documents', 'list.documents')),
    description=LISTING_TEXTS['listing_description'],
    previews=(('save', TEXT_PREVIEW),),
)

WRITE_LISTING = Workflow(
    slug='chat-01-write-a-product-listing',
    nodes=(
        Node('front', HostNode.IMAGE, {'image': ''}, title=SHARED_TEXTS['front']),
        Node('spec', ATTACH_DOCUMENT, {'file': ''}, title=SHARED_TEXTS['spec']),
        Node('listing', LISTING.name),
    ),
    links=(('front.IMAGE', 'listing.images'), ('spec.documents', 'listing.documents')),
    stacks=(
        (Group(SHARED_TEXTS['input'], (('front', 'spec'),), note=LISTING_TEXTS['input']),),
        (Group(SHARED_TEXTS['listing'], (('listing',),), STAGE_COLOUR, LISTING_TEXTS['listing']),),
    ),
    subgraphs=(LISTING,),
)

FACTS = Subgraph(
    name=SHARED_TEXTS['facts'],
    nodes=(
        Node(
            'ask',
            CHAT_ASK,
            {
                'model': GEMINI_FLASH,
                'reasoning_effort': 'low',
                'prompt': 'List the facts a shopper can see in this photo, one per line: what it is, its colors, and '
                'its materials.',
            },
            is_paid=True,
        ),
        Node('show', HostNode.PREVIEW),
    ),
    links=(('ask.text', 'show.source'),),
    columns=(('ask',), ('show',)),
    inputs=(('images', 'ask.images'),),
    outputs=(('conversation', 'ask.conversation'),),
    description=SCRIPT_TEXTS['facts_description'],
    previews=(('show', TEXT_PREVIEW),),
)

HOST_SCRIPT = Subgraph(
    name=SHARED_TEXTS['host_script'],
    nodes=(
        Node(
            'write',
            CHAT_ASK,
            {
                'model': GPT_LUNA,
                'prompt': 'Write a 30-second live-shopping script about this product from those facts.',
                'system_prompt': 'You are a warm, upbeat live-shopping host. Speak to the viewer, and invent nothing.',
            },
            is_paid=True,
        ),
        Node('save', HostNode.SAVE_TEXT, {'filename_prefix': 'text/kie/host-script'}),
    ),
    links=(('write.text', 'save.text'),),
    columns=(('write',), ('save',)),
    inputs=(('conversation', 'write.conversation'),),
    description=SCRIPT_TEXTS['host_script_description'],
    previews=(('save', TEXT_PREVIEW),),
)

WRITE_SCRIPT = Workflow(
    slug='chat-02-write-a-host-script',
    nodes=(
        Node('front', HostNode.IMAGE, {'image': ''}, title=SHARED_TEXTS['front']),
        Node('facts', FACTS.name),
        Node('script', HOST_SCRIPT.name),
    ),
    links=(('front.IMAGE', 'facts.images'), ('facts.conversation', 'script.conversation')),
    stacks=(
        (Group(SHARED_TEXTS['input'], (('front',),), note=SCRIPT_TEXTS['input']),),
        (Group(SHARED_TEXTS['facts'], (('facts',),), STAGE_COLOUR, SCRIPT_TEXTS['facts']),),
        (Group(SHARED_TEXTS['host_script'], (('script',),), STAGE_COLOUR, SCRIPT_TEXTS['host_script']),),
    ),
    subgraphs=(FACTS, HOST_SCRIPT),
)

CHAT_WORKFLOWS = (WRITE_LISTING, WRITE_SCRIPT)

__all__ = ['CHAT_WORKFLOWS']
