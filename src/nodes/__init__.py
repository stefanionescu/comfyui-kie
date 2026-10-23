"""Register the extension's nodes in menu order."""

from comfy_api.latest import io

from .files import FileAdd
from .model import ModelInfo
from .download import TaskDownload
from .generate import AudioGenerate, ImageGenerate, VideoGenerate

NODE_TYPES: tuple[type[io.ComfyNode], ...] = (
    ImageGenerate,
    VideoGenerate,
    AudioGenerate,
    FileAdd,
    TaskDownload,
    ModelInfo,
)

__all__ = ['NODE_TYPES']
