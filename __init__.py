"""Load the KIE nodes and their local routes through ComfyUI's extension entry point."""

from __future__ import annotations

from typing import override

from comfy_api.latest import ComfyExtension, io

from .src.nodes import NODE_TYPES
from .src.comfy.routes import register_routes

WEB_DIRECTORY = './web'


class Extension(ComfyExtension):
    """Register the local routes, and list the nodes."""

    @override
    async def on_load(self) -> None:
        """Register the local routes of the settings dialog."""
        register_routes()

    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        """Return the node classes in menu order."""
        return list(NODE_TYPES)


async def comfy_entrypoint() -> Extension:
    """Hand ComfyUI the extension."""
    return Extension()


__all__ = ['WEB_DIRECTORY', 'comfy_entrypoint']
