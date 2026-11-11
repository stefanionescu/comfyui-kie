"""Describe a workflow as nodes, links, groups, and the subgraphs it places."""

from __future__ import annotations

import uuid
from types import MappingProxyType
from typing import TYPE_CHECKING
from dataclasses import dataclass

from scripts.workflows.page.config import INPUT_COLOUR

if TYPE_CHECKING:
    from collections.abc import Mapping

    from scripts.types import WidgetValue

NO_VALUES: Mapping[str, WidgetValue] = MappingProxyType({})
NAMESPACE = uuid.UUID('72ee9f58-7bbd-418b-af1f-7f48a5f198bf')


@dataclass(frozen=True, slots=True)
class Node:
    """One node, with the widget values that differ from its defaults; a bypassed node ships switched off.

    Attributes:
        key: The name that links and columns use for the node.
        kind: The node ID, or the name of the subgraph the node places.
        values: The widget values that differ from the defaults, keyed by widget name.
        title: The title shown on the node, when the node has one.
        is_paid: Whether the node gets the colours of a paid node.
        is_bypassed: Whether the node ships switched off.

    """

    key: str
    kind: str
    values: Mapping[str, WidgetValue] = NO_VALUES
    title: str = ''
    is_paid: bool = False
    is_bypassed: bool = False


@dataclass(frozen=True, slots=True)
class Group:
    """One titled frame around columns of nodes, with a note above it that says what the group does.

    Attributes:
        title: The title of the frame.
        columns: The node keys of each column, from left to right.
        colour: The colour of the frame.
        note: The text of the note above the frame.

    """

    title: str
    columns: tuple[tuple[str, ...], ...]
    colour: str = INPUT_COLOUR
    note: str = ''


@dataclass(frozen=True, slots=True)
class Subgraph:
    """A reusable graph placed as one node; each link runs from `node.output` to `node.input`.

    Attributes:
        name: The name of the subgraph, which is also the kind of the node that places it.
        nodes: The nodes inside the subgraph.
        links: The links between the inner nodes.
        columns: The node keys of each column of the inner layout.
        inputs: The exposed inputs, each as a name and the `node.input` it feeds.
        outputs: The exposed outputs, each as a name and the `node.output` it reads.
        description: The text that describes the subgraph in ComfyUI.
        previews: The previews shown on the placed node, each as a node key and a preview name.

    """

    name: str
    nodes: tuple[Node, ...]
    links: tuple[tuple[str, str], ...]
    columns: tuple[tuple[str, ...], ...] = ()
    inputs: tuple[tuple[str, str], ...] = ()
    outputs: tuple[tuple[str, str], ...] = ()
    description: str = ''
    # The previews shown on the placed node, as `node key` and preview name.
    previews: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class Workflow:
    """One shipped workflow; each link runs from `node.output` to `node.input`.

    Attributes:
        slug: The name of the workflow file, without its extension.
        nodes: The nodes the workflow places.
        links: The links between the nodes.
        stacks: The stacks of groups, placed side by side.
        subgraphs: The subgraphs the workflow defines.

    """

    slug: str
    nodes: tuple[Node, ...]
    links: tuple[tuple[str, str], ...]
    stacks: tuple[tuple[Group, ...], ...]
    subgraphs: tuple[Subgraph, ...] = ()


__all__ = ['NAMESPACE', 'NO_VALUES', 'Group', 'Node', 'Subgraph', 'Workflow']
