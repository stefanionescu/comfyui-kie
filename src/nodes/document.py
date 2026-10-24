"""Chat: Attach Document, which attaches a PDF or text file from the input folder of ComfyUI to Chat: Ask."""

from __future__ import annotations

from typing import TYPE_CHECKING, override
import asyncio
from pathlib import Path

import folder_paths
from comfy_api.latest import io

from ..state.errors import KIEError, ErrorCode
from ..comfy.runtime import CONFIGURATION
from ..comfy.documents import read_document, list_documents
from ..config.namespace import MENUS, NODE_PREFIX, SOCKET_TYPES
from ..config.messages.chat import DOCUMENT_MISSING

if TYPE_CHECKING:
    from ..state.chat import Document


class ChatAttachDocument(io.ComfyNode):
    """Add one file to the documents it receives, the way the input-file nodes of ComfyUI chain."""

    @classmethod
    @override
    def define_schema(cls) -> io.Schema:
        """List the documents of the input folder when ComfyUI builds the node definitions; the R key reads it again."""
        return io.Schema(
            node_id=f'{NODE_PREFIX}{cls.__name__}',
            display_name='Chat: Attach Document',
            category=MENUS['CHAT'],
            description="Attach a PDF or text file from ComfyUI's input folder to Chat: Ask.",
            inputs=[
                io.Combo.Input(
                    'file',
                    options=list_documents(),
                    tooltip="A PDF, text, Markdown, CSV, or JSON file at the top of ComfyUI's input folder.",
                ),
                io.Custom(SOCKET_TYPES['DOCUMENTS']).Input(
                    'documents',
                    optional=True,
                    tooltip='Connect another Chat: Attach Document to send several documents.',
                ),
            ],
            outputs=[io.Custom(SOCKET_TYPES['DOCUMENTS']).Output('documents', display_name='documents')],
        )

    @classmethod
    @override
    def validate_inputs(cls, **_inputs: object) -> bool:
        """Take a file added after ComfyUI built the node definitions; the run reads the folder itself."""
        return True

    @classmethod
    @override
    def fingerprint_inputs(cls, *, file: str = '', **_inputs: object) -> str:
        """Run again when someone edits, replaces, or removes the file."""
        path = Path(folder_paths.get_annotated_filepath(file)) if file else None
        if path is None or not path.is_file():
            return file
        stat = path.stat()
        return f'{file}:{stat.st_mtime_ns}:{stat.st_size}'

    @classmethod
    @override
    async def execute(  # pyright: ignore[reportIncompatibleMethodOverride] # reason: ComfyUI calls execute with the inputs the schema declares.
        cls, *, file: str = '', documents: tuple[Document, ...] = ()
    ) -> io.NodeOutput:
        """Read the file off the event loop and add it after the earlier documents; the node needs no key."""
        if not file:
            raise KIEError(ErrorCode.INVALID_INPUT, DOCUMENT_MISSING)
        configuration = await asyncio.to_thread(CONFIGURATION.read_configuration)
        document = await asyncio.to_thread(read_document, file, configuration.settings.max_upload_megabytes)
        return io.NodeOutput((*documents, document))


__all__ = ['ChatAttachDocument']
