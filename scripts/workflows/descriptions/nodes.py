"""The node IDs the shipped workflows place most."""

from src.config.namespace import NODE_PREFIX

IMAGE_GENERATE = f'{NODE_PREFIX}ImageGenerate'
VIDEO_GENERATE = f'{NODE_PREFIX}VideoGenerate'
AUDIO_GENERATE = f'{NODE_PREFIX}AudioGenerate'
CHAT_ASK = f'{NODE_PREFIX}ChatAsk'
ATTACH_DOCUMENT = f'{NODE_PREFIX}ChatAttachDocument'
FILE_ADD = f'{NODE_PREFIX}FileAdd'
TASK_DOWNLOAD = f'{NODE_PREFIX}TaskDownload'
MODEL_INFO = f'{NODE_PREFIX}ModelInfo'

__all__ = [
    'ATTACH_DOCUMENT',
    'AUDIO_GENERATE',
    'CHAT_ASK',
    'FILE_ADD',
    'IMAGE_GENERATE',
    'MODEL_INFO',
    'TASK_DOWNLOAD',
    'VIDEO_GENERATE',
]
