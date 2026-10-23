"""What each node runs: the kinds of model, how KIE's task types map to them, and the model each node starts with."""

# The node that runs each kind of model, as messages name it.
KIND_NODES = {
    'image': 'Image: Generate',
    'video': 'Video: Generate',
    'audio': 'Audio: Generate',
    'chat': 'Chat: Ask',
}

# What each of KIE's task types makes. A model whose task types make a video is a video model, even when it also
# takes images, because its output is a video.
TASK_TYPE_KINDS = {
    'Text to Image': 'image',
    'Image to Image': 'image',
    'Image Editing': 'image',
    'Text to Video': 'video',
    'Image to Video': 'video',
    'Video to Video': 'video',
    'Video Editing': 'video',
    'Lip Sync': 'video',
    'Speech to Video': 'video',
    'Audio to Audio': 'audio',
    'Text to Music': 'audio',
    'Text to Speech': 'audio',
    'Chat': 'chat',
}

# The kind a model takes when its task types name several, first match first.
KIND_ORDER = ('video', 'audio', 'image', 'chat')

# The model each node starts with: current, and it runs with only the main text box of the node.
DEFAULT_MODELS = {
    'image': 'gpt-image-2-5-sunburst-text-to-image',
    'video': 'wan/3-0-video',
    'audio': 'elevenlabs/text-to-speech-turbo-2-5',
    'chat': 'gpt-6-luna',
}

# The route of every job model; a model with another route is a chat model, or uses an API the extension leaves out.
JOB_ROUTE = '/api/v1/jobs/createTask'

# The chat formats, by the end of a chat model's route.
CHAT_FORMATS = {
    '/v1/responses': 'responses',
    '/v1/messages': 'messages',
    '/v1/chat/completions': 'completions',
    ':streamGenerateContent': 'gemini',
}

# KIE's catalog and schema reads share one budget of one request a second per account, so reads keep this spacing.
READ_SPACING_SECONDS = 1.1

# A schema's chain of references longer than this is a loop, not a schema.
MAX_REFERENCES = 8

__all__ = [
    'CHAT_FORMATS',
    'DEFAULT_MODELS',
    'JOB_ROUTE',
    'KIND_NODES',
    'KIND_ORDER',
    'MAX_REFERENCES',
    'READ_SPACING_SECONDS',
    'TASK_TYPE_KINDS',
]
