"""The image workflows: design a host and pose them again, cut out a product, and make a poster series."""

import json

from scripts.nodes.host import HostNode
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.page.config import STAGE_COLOUR, IMAGE_PREVIEW
from scripts.workflows.descriptions.nodes import FILE_ADD, MODEL_INFO, IMAGE_GENERATE
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.descriptions.texts import SHARED_TEXTS

NANO_BANANA_PRO = 'nano-banana-pro'
QWEN_IMAGE = 'qwen/text-to-image'
TOPAZ_UPSCALE = 'topaz/image-upscale'
RECRAFT_CUT_OUT = 'recraft/remove-background'
FLUX_KLEIN = 'flux-3/klein-text-to-image'
# A portrait frame for the host, as a named setting set to custom.
PORTRAIT = {'aspect_ratio': 'custom', 'aspect_ratio.value': '3:4'}
TURN_PROMPT = 'The same host in a three-quarter view, waving at the camera, with the same outfit, hair, and background.'
HOST_TEXTS = WORKFLOW_TEXTS['image-01-design-a-host']
CUT_OUT_TEXTS = WORKFLOW_TEXTS['image-02-cut-out-a-product']
SERIES_TEXTS = WORKFLOW_TEXTS['image-03-make-a-poster-series']

DESIGN = Subgraph(
    name=SHARED_TEXTS['design'],
    nodes=(
        Node(
            'prompt',
            HostNode.FORMAT,
            {
                'f_string': (
                    'Studio portrait of a live-shopping host: {a} Waist up, facing the camera, plain light gray '
                    'background, soft light.'
                )
            },
        ),
        Node('draw', IMAGE_GENERATE, {'model': NANO_BANANA_PRO, **PORTRAIT}, is_paid=True),
        Node('save', HostNode.SAVE_IMAGE, {'filename_prefix': 'image/kie/host'}),
    ),
    links=(('prompt.STRING', 'draw.prompt'), ('draw.images', 'save.images')),
    columns=(('prompt',), ('draw',), ('save',)),
    inputs=(('host', 'prompt.values.a'),),
    outputs=(('files', 'draw.files'),),
    description=HOST_TEXTS['design_description'],
    previews=(('save', IMAGE_PREVIEW),),
)

TURN = Subgraph(
    name=SHARED_TEXTS['turn'],
    nodes=(
        Node('add', FILE_ADD, {'field': 'image_input'}),
        Node('edit', IMAGE_GENERATE, {'model': NANO_BANANA_PRO, **PORTRAIT, 'prompt': TURN_PROMPT}, is_paid=True),
        Node('save', HostNode.SAVE_IMAGE, {'filename_prefix': 'image/kie/host-waving'}),
    ),
    links=(('add.files', 'edit.files'), ('edit.images', 'save.images')),
    columns=(('add',), ('edit',), ('save',)),
    inputs=(('files', 'add.file'),),
    description=HOST_TEXTS['turn_description'],
    previews=(('save', IMAGE_PREVIEW),),
)

DESIGN_HOST = Workflow(
    slug='image-01-design-a-host',
    nodes=(
        Node(
            'host',
            HostNode.TEXT_BLOCK,
            {
                'value': (
                    'A cheerful woman in her late twenties with shoulder-length auburn hair, a mustard knit sweater, '
                    'and small gold hoop earrings.'
                )
            },
            title=SHARED_TEXTS['host'],
        ),
        Node('design', DESIGN.name),
        Node('turn', TURN.name),
    ),
    links=(('host.STRING', 'design.host'), ('design.files', 'turn.files')),
    stacks=(
        (Group(SHARED_TEXTS['input'], (('host',),), note=HOST_TEXTS['input']),),
        (Group(SHARED_TEXTS['design'], (('design',),), STAGE_COLOUR, HOST_TEXTS['design']),),
        (Group(SHARED_TEXTS['turn'], (('turn',),), STAGE_COLOUR, HOST_TEXTS['turn']),),
    ),
    subgraphs=(DESIGN, TURN),
)

PHOTO = Subgraph(
    name=SHARED_TEXTS['photo'],
    nodes=(
        Node(
            'draw',
            IMAGE_GENERATE,
            {
                'model': QWEN_IMAGE,
                'guidance_scale': 'custom',
                'guidance_scale.value': 4.0,
                'num_inference_steps': 'custom',
                'num_inference_steps.value': 30,
                'negative_prompt': 'text, watermark, people',
                'arguments': json.dumps({'image_size': 'square_hd'}, indent=2),
            },
            is_paid=True,
        ),
        Node('look', HostNode.PREVIEW_IMAGE),
    ),
    links=(('draw.images', 'look.images'),),
    columns=(('draw',), ('look',)),
    inputs=(('product', 'draw.prompt'),),
    outputs=(('files', 'draw.files'),),
    description=CUT_OUT_TEXTS['photo_description'],
    previews=(('look', IMAGE_PREVIEW),),
)

UPSCALE = Subgraph(
    name=SHARED_TEXTS['upscale'],
    nodes=(
        Node('add', FILE_ADD, {'field': 'image_url'}),
        Node(
            'up',
            IMAGE_GENERATE,
            {'model': TOPAZ_UPSCALE, 'prompt': '', 'arguments': json.dumps({'upscale_factor': '2'}, indent=2)},
            is_paid=True,
        ),
        Node('save', HostNode.SAVE_IMAGE, {'filename_prefix': 'image/kie/product-large'}),
    ),
    links=(('add.files', 'up.files'), ('up.images', 'save.images')),
    columns=(('add',), ('up',), ('save',)),
    inputs=(('files', 'add.file'),),
    outputs=(('files', 'up.files'),),
    description=CUT_OUT_TEXTS['upscale_description'],
    previews=(('save', IMAGE_PREVIEW),),
)

CUT_OUT = Subgraph(
    name=SHARED_TEXTS['cut_out'],
    nodes=(
        Node('add', FILE_ADD, {'field': 'image'}),
        Node('cut', IMAGE_GENERATE, {'model': RECRAFT_CUT_OUT, 'prompt': ''}, is_paid=True),
        Node('first', HostNode.LIST_ITEM),
        Node('first_mask', HostNode.LIST_ITEM),
        Node('join', HostNode.JOIN_ALPHA),
        Node('save', HostNode.SAVE_IMAGE, {'filename_prefix': 'image/kie/product-cut-out'}),
    ),
    links=(
        ('add.files', 'cut.files'),
        ('cut.images', 'first.list'),
        ('cut.masks', 'first_mask.list'),
        ('first.*', 'join.image'),
        ('first_mask.*', 'join.alpha'),
        ('join.IMAGE', 'save.images'),
    ),
    columns=(('add',), ('cut',), ('first', 'first_mask'), ('join',), ('save',)),
    inputs=(('files', 'add.file'),),
    description=CUT_OUT_TEXTS['cut_out_description'],
    previews=(('save', IMAGE_PREVIEW),),
)

CUT_OUT_PRODUCT = Workflow(
    slug='image-02-cut-out-a-product',
    nodes=(
        Node(
            'product',
            HostNode.TEXT_BLOCK,
            {
                'value': (
                    'A pair of white canvas sneakers with red laces, side view, on a plain white background, soft '
                    'studio light.'
                )
            },
            title=SHARED_TEXTS['product'],
        ),
        Node('photo', PHOTO.name),
        Node('upscale', UPSCALE.name),
        Node('cut_out', CUT_OUT.name),
    ),
    links=(
        ('product.STRING', 'photo.product'),
        ('photo.files', 'upscale.files'),
        ('upscale.files', 'cut_out.files'),
    ),
    stacks=(
        (Group(SHARED_TEXTS['input'], (('product',),), note=CUT_OUT_TEXTS['input']),),
        (Group(SHARED_TEXTS['photo'], (('photo',),), STAGE_COLOUR, CUT_OUT_TEXTS['photo']),),
        (Group(SHARED_TEXTS['upscale'], (('upscale',),), STAGE_COLOUR, CUT_OUT_TEXTS['upscale']),),
        (Group(SHARED_TEXTS['cut_out'], (('cut_out',),), STAGE_COLOUR, CUT_OUT_TEXTS['cut_out']),),
    ),
    subgraphs=(PHOTO, UPSCALE, CUT_OUT),
)

SERIES = Subgraph(
    name=SHARED_TEXTS['series'],
    nodes=(
        Node(
            'draw',
            IMAGE_GENERATE,
            {
                'model': FLUX_KLEIN,
                **PORTRAIT,
                'num_images': 'custom',
                'num_images.value': 4,
                'seed': 'custom',
                'seed.value': 7,
            },
            is_paid=True,
        ),
        Node('save', HostNode.SAVE_IMAGE, {'filename_prefix': 'image/kie/poster-series'}),
    ),
    links=(('draw.images', 'save.images'),),
    columns=(('draw',), ('save',)),
    inputs=(('brief', 'draw.prompt'),),
    description=SERIES_TEXTS['series_description'],
    previews=(('save', IMAGE_PREVIEW),),
)

POSTER_SERIES = Workflow(
    slug='image-03-make-a-poster-series',
    nodes=(
        Node(
            'brief',
            HostNode.TEXT_BLOCK,
            {
                'value': (
                    'A flat illustration travel poster for the seaside town "Port Ellis", with the name of the town at '
                    'the top, a lighthouse, and sailboats at sunset.'
                )
            },
            title=SHARED_TEXTS['brief'],
        ),
        Node('info', MODEL_INFO, {'model': FLUX_KLEIN}),
        Node('row', HostNode.PREVIEW, title=SHARED_TEXTS['info']),
        Node('series', SERIES.name),
    ),
    links=(('brief.STRING', 'series.brief'), ('info.info', 'row.source')),
    stacks=(
        (
            Group(SHARED_TEXTS['input'], (('brief',),), note=SERIES_TEXTS['input']),
            Group(SHARED_TEXTS['model'], (('info',), ('row',)), note=SERIES_TEXTS['model']),
        ),
        (Group(SHARED_TEXTS['series'], (('series',),), STAGE_COLOUR, SERIES_TEXTS['series']),),
    ),
    subgraphs=(SERIES,),
)

IMAGE_WORKFLOWS = (DESIGN_HOST, CUT_OUT_PRODUCT, POSTER_SERIES)

__all__ = ['IMAGE_WORKFLOWS', 'PHOTO']
