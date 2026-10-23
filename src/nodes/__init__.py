"""Register the extension's nodes in menu order."""

from comfy_api.latest import io

from .model import ModelInfo

NODE_TYPES: tuple[type[io.ComfyNode], ...] = (ModelInfo,)

__all__ = ['NODE_TYPES']
