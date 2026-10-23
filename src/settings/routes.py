"""Serve private settings and key changes through guarded local routes."""

import re
import asyncio
from dataclasses import dataclass

from aiohttp import web

from .body import read_body
from .store import ConfigurationStore
from ..state import Json
from .access import build_local_route
from ..config.patterns import REVISION_PATTERN
from ..config.security import ROUTES
from ..config.messages.requests import CLEAR_KEY_BODY, SINGLE_KEY_REQUIRED, SETTINGS_REVISION_REQUIRED

_REVISION = re.compile(REVISION_PATTERN)


@dataclass(frozen=True, slots=True)
class ConfigurationRoutes:
    """The settings routes, registered once while ComfyUI loads the extension.

    Attributes:
        store: The private settings and key.
        is_multi_user: Whether ComfyUI serves several users, which allows no changes.

    """

    store: ConfigurationStore
    is_multi_user: bool

    async def save_settings(self, request: web.Request) -> dict[str, Json]:
        """Check the changed settings, and save them against the revision the dialog read."""
        document = await read_body(request)
        revision = document.get('revision')
        changes = document.get('settings')
        if document.keys() != {'revision', 'settings'} or not isinstance(changes, dict):
            raise web.HTTPBadRequest(text=SETTINGS_REVISION_REQUIRED)
        if not isinstance(revision, str) or not _REVISION.match(revision):
            raise web.HTTPBadRequest(text=SETTINGS_REVISION_REQUIRED)
        return await asyncio.to_thread(self.store.save_settings, changes, revision)

    async def save_credential(self, request: web.Request) -> dict[str, Json]:
        """Accept one API key, and save it only in the private state folder."""
        document = await read_body(request)
        value = document.get('api_key')
        if document.keys() != {'api_key'} or not isinstance(value, str):
            raise web.HTTPBadRequest(text=SINGLE_KEY_REQUIRED)
        return await asyncio.to_thread(self.store.save_credential, value)

    async def delete_credential(self, request: web.Request) -> dict[str, Json]:
        """Remove the saved key, and refuse a request that sends content."""
        if request.can_read_body:
            raise web.HTTPBadRequest(text=CLEAR_KEY_BODY)
        return await asyncio.to_thread(self.store.delete_credential)

    def register(self, routes: web.RouteTableDef) -> None:
        """Register the guarded status, settings, key-save, and key-removal routes."""
        policy = {'is_multi_user': self.is_multi_user}
        read_status = build_local_route(
            lambda _request: asyncio.to_thread(self.store.read_status), is_mutation=False, **policy
        )
        routes.get(ROUTES['STATUS'])(read_status)
        routes.patch(ROUTES['SETTINGS'])(build_local_route(self.save_settings, is_mutation=True, **policy))
        routes.put(ROUTES['CREDENTIAL'])(build_local_route(self.save_credential, is_mutation=True, **policy))
        routes.delete(ROUTES['CREDENTIAL'])(build_local_route(self.delete_credential, is_mutation=True, **policy))


__all__ = ['ConfigurationRoutes']
