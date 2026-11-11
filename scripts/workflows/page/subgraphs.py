"""Turn subgraph descriptions into the JSON ComfyUI saves."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, cast

from scripts.workflows.page.graph import NAMESPACE, Node
from scripts.workflows.page.sizes import measure
from scripts.workflows.page.config import PORT_GAP, PORT_WIDTH, INNER_ORIGIN, SUBGRAPH_ID_STEP
from scripts.workflows.page.layout import place_columns
from scripts.workflows.page.serialize import find_slot, encode_links, encode_nodes

if TYPE_CHECKING:
    from scripts.types import Json
    from scripts.workflows.page.graph import Subgraph
    from scripts.workflows.page.palette import Palette


def _encode_ports(
    subgraph: Subgraph, subgraph_id: str, entries: dict[str, Json], records: list[Json], side: str
) -> list[Json]:
    """Link the exposed inputs or outputs to the inner nodes.

    Args:
        subgraph: The subgraph whose ports get links.
        subgraph_id: The ID of the subgraph, which the port IDs come from.
        entries: The serialized inner nodes, keyed by node key. The function writes the link numbers into them.
        records: The link records so far. The function adds one record for each port.
        side: The ports to link, `inputs` or `outputs`.

    Returns:
        The serialized ports of that side.

    """
    ports: list[Json] = []
    port_node, inner_side = (-10, 'inputs') if side == 'inputs' else (-20, 'outputs')
    for index, (name, socket) in enumerate(getattr(subgraph, side)):
        key, socket_name = socket.split('.', 1)
        entry = entries[key]
        position = find_slot(entry, inner_side, socket_name)
        number = len(records) + 1
        inner = cast('list[Json]', entry[inner_side])[position]
        if side == 'inputs':
            inner['link'] = number
            record = {'origin_id': port_node, 'origin_slot': index, 'target_id': entry['id'], 'target_slot': position}
        else:
            cast('list[int]', inner['links']).append(number)
            record = {'origin_id': entry['id'], 'origin_slot': position, 'target_id': port_node, 'target_slot': index}
        records.append({'id': number, **record, 'type': inner['type']})
        port_id = str(uuid.uuid5(NAMESPACE, f'{subgraph_id}.{side}.{name}'))
        ports.append({'id': port_id, 'name': name, 'type': inner['type'], 'linkIds': [number], 'pos': [0, 0]})
    return ports


def read_preview_exposures(subgraph: Subgraph, position: int) -> list[Json]:
    """List the previews of nodes inside a subgraph that its placed node shows, such as a saved image.

    The inner node IDs follow the numbering `encode_subgraph` gives them.

    Args:
        subgraph: The subgraph whose previews are listed.
        position: The position of the subgraph in its workflow, which sets the IDs of its inner nodes.

    Returns:
        One entry for each preview, with the ID of the inner node that makes it.

    """
    keys = [node.key for node in subgraph.nodes]
    first_id = position * SUBGRAPH_ID_STEP + 1
    return [
        {'name': name, 'sourceNodeId': str(first_id + keys.index(key)), 'sourcePreviewName': name}
        for key, name in subgraph.previews
    ]


def encode_subgraph(subgraph: Subgraph, palette: Palette, position: int) -> Json:
    """Serialize one subgraph definition with its input and output ports.

    Args:
        subgraph: The subgraph to serialize.
        palette: The table that describes the inner nodes and holds the ID of the subgraph.
        position: The position of the subgraph in its workflow, which sets the IDs of its inner nodes.

    Returns:
        The subgraph definition as ComfyUI saves it.

    """
    subgraph_id = palette.ids[subgraph.name]
    # The input ports link sockets too, so the growing rows they feed show those slots.
    targets = [end for _start, end in (*subgraph.links, *subgraph.inputs)]
    linked = [target.split('.', 1) for target in targets]
    sizes = {
        node.key: measure(
            node.kind,
            palette.find_schema(node),
            node.values,
            frozenset(socket for key, socket in linked if key == node.key),
        )
        for node in subgraph.nodes
    }
    placed = place_columns(subgraph.columns, sizes, INNER_ORIGIN)
    boxes = {key: (box.x, box.y, box.width, box.height) for key, box in placed.items()}
    entries = encode_nodes(subgraph.nodes, palette, boxes, targets, position * SUBGRAPH_ID_STEP + 1)
    records = encode_links(entries, subgraph.links)
    inputs = _encode_ports(subgraph, subgraph_id, entries, records, 'inputs')
    outputs = _encode_ports(subgraph, subgraph_id, entries, records, 'outputs')
    right = max(box.x + box.width for box in placed.values()) + PORT_GAP
    for index, port in enumerate(inputs):
        port['pos'] = [INNER_ORIGIN[0] - PORT_GAP, INNER_ORIGIN[1] + 20 * index]
    for index, port in enumerate(outputs):
        port['pos'] = [right, INNER_ORIGIN[1] + 20 * index]
    return {
        'id': subgraph_id,
        'version': 1,
        'state': {
            'lastGroupId': 0,
            'lastNodeId': position * SUBGRAPH_ID_STEP + len(entries),
            'lastLinkId': len(records),
            'lastRerouteId': 0,
        },
        'revision': 0,
        'config': {},
        'name': subgraph.name,
        'inputNode': {
            'id': -10,
            'bounding': [
                INNER_ORIGIN[0] - PORT_GAP - PORT_WIDTH,
                INNER_ORIGIN[1],
                PORT_WIDTH,
                20 * max(1, len(inputs)),
            ],
        },
        'outputNode': {'id': -20, 'bounding': [right, INNER_ORIGIN[1], PORT_WIDTH, 20 * max(1, len(outputs))]},
        'inputs': inputs,
        'outputs': outputs,
        'widgets': [],
        'nodes': list(entries.values()),
        'groups': [],
        'links': records,
        'extra': {'description': subgraph.description} if subgraph.description else {},
    }


def encode_blueprint(subgraph: Subgraph, palette: Palette, category: str) -> Json:
    """Serialize one subgraph as a blueprint for ComfyUI's node library: one node that places it, and its definition.

    ComfyUI names the blueprint after its file and lists it under Subgraph Blueprints, in its category, with its
    description.

    Args:
        subgraph: The subgraph the blueprint holds.
        palette: The table that describes the subgraph and its inner nodes.
        category: The node menu that lists the blueprint.

    Returns:
        The blueprint as the JSON ComfyUI saves.

    """
    node = Node('blueprint', subgraph.name)
    size = measure(node.kind, palette.find_schema(node), node.values, frozenset())
    entry = encode_nodes((node,), palette, {node.key: (0, 0, *size)}, [])[node.key]
    exposures = read_preview_exposures(subgraph, 1)
    if exposures:
        cast('Json', entry['properties'])['previewExposures'] = exposures
    definition = encode_subgraph(subgraph, palette, 1) | {'category': category, 'description': subgraph.description}
    return {
        'id': str(uuid.uuid5(NAMESPACE, f'blueprint.{subgraph.name}')),
        'revision': 0,
        'last_node_id': 1,
        'last_link_id': 0,
        'nodes': [entry],
        'links': [],
        'groups': [],
        'config': {},
        'extra': {},
        'version': 0.4,
        'definitions': {'subgraphs': [definition]},
    }


__all__ = ['encode_blueprint', 'encode_subgraph', 'read_preview_exposures']
