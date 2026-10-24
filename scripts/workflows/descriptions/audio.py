"""The audio workflows: voice a script, and write a song."""

import json

from scripts.nodes.host import HostNode
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.workflows.page.config import STAGE_COLOUR, AUDIO_PREVIEW
from scripts.workflows.descriptions.nodes import AUDIO_GENERATE
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.descriptions.texts import SHARED_TEXTS

ELEVENLABS_TURBO = 'elevenlabs/text-to-speech-turbo-2-5'
SUNO = 'ai-music-api/generate'
SONG_ARGUMENTS = json.dumps({'custom_mode': False, 'instrumental': False, 'model': 'V4_5'}, indent=2)
SCRIPT_TEXTS = WORKFLOW_TEXTS['audio-01-voice-a-script']
SONG_TEXTS = WORKFLOW_TEXTS['audio-02-write-a-song']

SPEAK = Subgraph(
    name=SHARED_TEXTS['speak'],
    nodes=(
        Node('say', AUDIO_GENERATE, {'model': ELEVENLABS_TURBO}, is_paid=True),
        Node('save', HostNode.SAVE_AUDIO, {'filename_prefix': 'audio/kie/script'}),
    ),
    links=(('say.audio', 'save.audio'),),
    columns=(('say',), ('save',)),
    inputs=(('script', 'say.text'),),
    outputs=(('files', 'say.files'),),
    description=SCRIPT_TEXTS['speak_description'],
    previews=(('save', AUDIO_PREVIEW),),
)

VOICE_SCRIPT = Workflow(
    slug='audio-01-voice-a-script',
    nodes=(
        Node(
            'script',
            HostNode.TEXT_BLOCK,
            {
                'value': (
                    'Welcome back, everyone! Today I have something special: a wool scarf in a warm winter tartan, '
                    'soft enough to wear all day.'
                )
            },
            title=SHARED_TEXTS['script'],
        ),
        Node('speak', SPEAK.name),
    ),
    links=(('script.STRING', 'speak.script'),),
    stacks=(
        (Group(SHARED_TEXTS['input'], (('script',),), note=SCRIPT_TEXTS['input']),),
        (Group(SHARED_TEXTS['speak'], (('speak',),), STAGE_COLOUR, SCRIPT_TEXTS['speak']),),
    ),
    subgraphs=(SPEAK,),
)

COMPOSE = Subgraph(
    name=SHARED_TEXTS['compose'],
    nodes=(
        Node('write', AUDIO_GENERATE, {'model': SUNO, 'voice': '', 'arguments': SONG_ARGUMENTS}, is_paid=True),
        Node('save', HostNode.SAVE_AUDIO, {'filename_prefix': 'audio/kie/song'}),
    ),
    links=(('write.audio', 'save.audio'),),
    columns=(('write',), ('save',)),
    inputs=(('song', 'write.prompt'),),
    description=SONG_TEXTS['compose_description'],
    previews=(('save', AUDIO_PREVIEW),),
)

WRITE_SONG = Workflow(
    slug='audio-02-write-a-song',
    nodes=(
        Node(
            'song',
            HostNode.TEXT_BLOCK,
            {'value': 'An upbeat acoustic pop jingle about a cozy winter scarf, with a warm female voice.'},
            title=SHARED_TEXTS['song'],
        ),
        Node('compose', COMPOSE.name),
    ),
    links=(('song.STRING', 'compose.song'),),
    stacks=(
        (Group(SHARED_TEXTS['input'], (('song',),), note=SONG_TEXTS['input']),),
        (Group(SHARED_TEXTS['compose'], (('compose',),), STAGE_COLOUR, SONG_TEXTS['compose']),),
    ),
    subgraphs=(COMPOSE,),
)

AUDIO_WORKFLOWS = (VOICE_SCRIPT, WRITE_SONG)

__all__ = ['AUDIO_WORKFLOWS', 'ELEVENLABS_TURBO']
