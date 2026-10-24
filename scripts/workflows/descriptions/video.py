"""The video workflows: animate a photo, show a product with a voice, and recover a video left running."""

import json

from scripts.nodes.host import HostNode
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.page.config import STAGE_COLOUR, IMAGE_PREVIEW, VIDEO_PREVIEW
from scripts.workflows.descriptions.audio import ELEVENLABS_TURBO
from scripts.workflows.descriptions.image import PHOTO
from scripts.workflows.descriptions.nodes import (
    FILE_ADD,
    TASK_DOWNLOAD,
    AUDIO_GENERATE,
    IMAGE_GENERATE,
    VIDEO_GENERATE,
)
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.descriptions.texts import SHARED_TEXTS

Z_IMAGE = 'z-image'
WAN_VIDEO = 'wan/3-0-video'
# Wan makes 1080P by default; the examples ask for five seconds at 480P.
WAN_SETTINGS = {'resolution': 'custom', 'resolution.value': '480P', 'duration': 'custom', 'duration.value': 5}
QUIET = json.dumps({'audio': False}, indent=2)
ANIMATE_TEXTS = WORKFLOW_TEXTS['video-01-animate-a-photo']
PRODUCT_TEXTS = WORKFLOW_TEXTS['video-02-show-a-product-with-a-voice']
RECOVER_TEXTS = WORKFLOW_TEXTS['video-03-recover-a-video']

PORTRAIT = Subgraph(
    name=SHARED_TEXTS['portrait'],
    nodes=(
        Node(
            'prompt',
            HostNode.FORMAT,
            {'f_string': 'Waist-up photo of a live-shopping host, vertical frame: {a} Looking at the camera.'},
        ),
        Node(
            'draw',
            IMAGE_GENERATE,
            {'model': Z_IMAGE, 'aspect_ratio': 'custom', 'aspect_ratio.value': '9:16'},
            is_paid=True,
        ),
        Node('look', HostNode.PREVIEW_IMAGE),
    ),
    links=(('prompt.STRING', 'draw.prompt'), ('draw.images', 'look.images')),
    columns=(('prompt',), ('draw',), ('look',)),
    inputs=(('host', 'prompt.values.a'),),
    outputs=(('files', 'draw.files'),),
    description=ANIMATE_TEXTS['portrait_description'],
    previews=(('look', IMAGE_PREVIEW),),
)

ANIMATE = Subgraph(
    name=SHARED_TEXTS['animate'],
    nodes=(
        Node('add', FILE_ADD, {'field': 'first_frame_url'}),
        Node(
            'film',
            VIDEO_GENERATE,
            {
                'model': WAN_VIDEO,
                **WAN_SETTINGS,
                'prompt': 'The host smiles, waves at the camera, and starts to talk.',
                'arguments': QUIET,
            },
            is_paid=True,
        ),
        Node('save', HostNode.SAVE_VIDEO, {'filename_prefix': 'video/kie/host'}),
    ),
    links=(('add.files', 'film.files'), ('film.video', 'save.video')),
    columns=(('add',), ('film',), ('save',)),
    inputs=(('files', 'add.file'),),
    description=ANIMATE_TEXTS['animate_description'],
    previews=(('save', VIDEO_PREVIEW),),
)

ANIMATE_PHOTO = Workflow(
    slug='video-01-animate-a-photo',
    nodes=(
        Node(
            'host',
            HostNode.TEXT_BLOCK,
            {
                'value': (
                    'A friendly man in his thirties with short dark hair and a navy linen shirt, in a bright studio.'
                )
            },
            title=SHARED_TEXTS['host'],
        ),
        Node('portrait', PORTRAIT.name),
        Node('animate', ANIMATE.name),
    ),
    links=(('host.STRING', 'portrait.host'), ('portrait.files', 'animate.files')),
    stacks=(
        (Group(SHARED_TEXTS['input'], (('host',),), note=ANIMATE_TEXTS['input']),),
        (Group(SHARED_TEXTS['portrait'], (('portrait',),), STAGE_COLOUR, ANIMATE_TEXTS['portrait']),),
        (Group(SHARED_TEXTS['animate'], (('animate',),), STAGE_COLOUR, ANIMATE_TEXTS['animate']),),
    ),
    subgraphs=(PORTRAIT, ANIMATE),
)

VOICE = Subgraph(
    name=SHARED_TEXTS['voice'],
    nodes=(Node('say', AUDIO_GENERATE, {'model': ELEVENLABS_TURBO}, is_paid=True),),
    links=(),
    columns=(('say',),),
    inputs=(('line', 'say.text'),),
    outputs=(('files', 'say.files'),),
    description=PRODUCT_TEXTS['voice_description'],
)

FILM = Subgraph(
    name=SHARED_TEXTS['film'],
    nodes=(
        Node('add_product', FILE_ADD, {'field': 'reference_image_urls'}),
        Node('add_voice', FILE_ADD, {'field': 'reference_audio_urls'}),
        Node(
            'film',
            VIDEO_GENERATE,
            {
                'model': WAN_VIDEO,
                **WAN_SETTINGS,
                'aspect_ratio': 'custom',
                'aspect_ratio.value': '9:16',
                'prompt': (
                    'A live-shopping host holds up the product from the reference image, looks at the camera, and '
                    'says the line from the reference audio.'
                ),
            },
            is_paid=True,
        ),
        Node('save', HostNode.SAVE_VIDEO, {'filename_prefix': 'video/kie/product-with-voice'}),
    ),
    links=(
        ('add_product.files', 'add_voice.files'),
        ('add_voice.files', 'film.files'),
        ('film.video', 'save.video'),
    ),
    columns=(('add_product', 'add_voice'), ('film',), ('save',)),
    inputs=(('product', 'add_product.file'), ('voice', 'add_voice.file')),
    description=PRODUCT_TEXTS['film_description'],
    previews=(('save', VIDEO_PREVIEW),),
)

SHOW_PRODUCT = Workflow(
    slug='video-02-show-a-product-with-a-voice',
    nodes=(
        Node(
            'product',
            HostNode.TEXT_BLOCK,
            {'value': 'A red ceramic coffee mug with a white handle, on a plain white background, studio light.'},
            title=SHARED_TEXTS['product'],
        ),
        Node(
            'line',
            HostNode.TEXT_BLOCK,
            {'value': 'This mug keeps your coffee warm all morning, and it comes in five colors.'},
            title=SHARED_TEXTS['line'],
        ),
        Node('photo', PHOTO.name),
        Node('voice', VOICE.name),
        Node('film', FILM.name),
    ),
    links=(
        ('product.STRING', 'photo.product'),
        ('line.STRING', 'voice.line'),
        ('photo.files', 'film.product'),
        ('voice.files', 'film.voice'),
    ),
    stacks=(
        (Group(SHARED_TEXTS['input'], (('product', 'line'),), note=PRODUCT_TEXTS['input']),),
        (
            Group(SHARED_TEXTS['photo'], (('photo',),), STAGE_COLOUR, PRODUCT_TEXTS['photo']),
            Group(SHARED_TEXTS['voice'], (('voice',),), STAGE_COLOUR, PRODUCT_TEXTS['voice']),
        ),
        (Group(SHARED_TEXTS['film'], (('film',),), STAGE_COLOUR, PRODUCT_TEXTS['film']),),
    ),
    subgraphs=(PHOTO, VOICE, FILM),
)

RECOVER_VIDEO = Workflow(
    slug='video-03-recover-a-video',
    nodes=(
        Node('download', TASK_DOWNLOAD, {'task': ''}),
        Node('save', HostNode.SAVE_VIDEO, {'filename_prefix': 'video/kie/recovered'}),
    ),
    links=(('download.video', 'save.video'),),
    stacks=((Group(SHARED_TEXTS['recover'], (('download',), ('save',)), STAGE_COLOUR, RECOVER_TEXTS['recover']),),),
)

VIDEO_WORKFLOWS = (ANIMATE_PHOTO, SHOW_PRODUCT, RECOVER_VIDEO)

__all__ = ['VIDEO_WORKFLOWS']
