"""Turn workflow descriptions into the JSON ComfyUI saves."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from scripts.workflows.page.sizes import list_shown_slots
from scripts.workflows.page.config import BYPASS_MODE, PAID_COLOURS, AUTOGROW_TYPE
from scripts.workflows.page.palette import Palette, read_slot_type
from scripts.workflows.page.widgets import encode_widget_values

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from scripts.types import Item, Json, Schema
    from scripts.workflows.page.graph import Node


def _encode_inputs(schema: Schema, linked: frozenset[str]) -> list[Json]:
    """Serialize the inputs of a node; a growing row shows its linked slots and one more.

    Args:
        schema: The description of the node.
        linked: The names of the inputs that links fill.

    Returns:
        One entry for each input socket, with no link yet.

    """
    inputs: list[Json] = []
    for item in cast('list[Item]', schema['inputs']):
        if item['type'] == AUTOGROW_TYPE:
            slot_type = read_slot_type(item)
            inputs += [
                {'label': slot.rsplit('.', 1)[1], 'name': slot, 'type': slot_type, 'link': None, 'shape': 7}
                for slot in list_shown_slots(str(item['name']), item, linked)
            ]
            continue
        entry: Json = {'name': item['name'], 'type': item['type'], 'link': None}
        if item.get('widget'):
            entry['widget'] = {'name': item['name']}
        elif item.get('optional'):
            entry['shape'] = 7
        inputs.append(entry)
    return inputs


def _encode_node(
    node: Node, number: int, palette: Palette, box: tuple[int, int, int, int], linked: frozenset[str]
) -> Json:
    """Serialize one node with nothing linked.

    Args:
        node: The node to serialize.
        number: The ID of the node in the file.
        palette: The table that describes the node.
        box: The x, y, width, and height of the node.
        linked: The names of the inputs of the node that links fill.

    Returns:
        The node as ComfyUI saves it.

    """
    schema = palette.find_schema(node)
    is_subgraph = node.kind in palette.subgraphs
    inputs = _encode_inputs(schema, linked)
    outputs: list[Json] = [
        {'name': item['name'], 'type': item['type'], **({'shape': 6} if item.get('is_list') else {}), 'links': []}
        for item in cast('list[Item]', schema['outputs'])
    ]
    kind = palette.ids[node.kind] if is_subgraph else node.kind
    entry: Json = {
        'id': number,
        'type': kind,
        'pos': [box[0], box[1]],
        'size': [box[2], box[3]],
        'flags': {},
        'order': number - 1,
        'mode': BYPASS_MODE if node.is_bypassed else 0,
        'inputs': inputs,
        'outputs': outputs,
        'properties': {} if is_subgraph else {'Node name for S&R': kind},
        'widgets_values': encode_widget_values(schema, node.values, node.kind),
    }
    if node.title or is_subgraph:
        entry['title'] = node.title or node.kind
    if node.is_paid:
        entry.update(PAID_COLOURS)
    return entry


def find_slot(entry: Json, side: str, name: str) -> int:
    """Find the position of a serialized input or output.

    Args:
        entry: The serialized node.
        side: The list to search, `inputs` or `outputs`.
        name: The name of the socket.

    Returns:
        The position of the socket in that list.

    Raises:
        KeyError: When the node has no socket of that name on that side.

    """
    sockets = cast('list[Json]', entry[side])
    index = next((index for index, socket in enumerate(sockets) if socket['name'] == name), None)
    if index is None:
        message = f'{entry["type"]} has no {side[:-1]} named {name}.'
        raise KeyError(message)
    return index


def encode_nodes(
    nodes: tuple[Node, ...],
    palette: Palette,
    boxes: Mapping[str, tuple[int, int, int, int]],
    targets: Sequence[str],
    first_id: int = 1,
) -> dict[str, Json]:
    """Serialize nodes with nothing linked yet; the targets are the `node.socket` names links will fill.

    Args:
        nodes: The nodes to serialize, in the order of their IDs.
        palette: The table that describes each node.
        boxes: The x, y, width, and height of each node, keyed by node key.
        targets: The `node.socket` names that links fill later.
        first_id: The ID of the first node. The IDs count up from it.

    Returns:
        The serialized nodes, keyed by node key.

    Raises:
        ValueError: When two nodes share a key.

    """
    linked = [target.split('.', 1) for target in targets]
    entries = {
        node.key: _encode_node(
            node,
            number,
            palette,
            boxes[node.key],
            frozenset(socket for key, socket in linked if key == node.key),
        )
        for number, node in enumerate(nodes, first_id)
    }
    if len(entries) != len(nodes):
        message = 'Give every node its own key.'
        raise ValueError(message)
    return entries


def encode_links(entries: Mapping[str, Json], links: tuple[tuple[str, str], ...]) -> list[Json]:
    """Link serialized nodes.

    Args:
        entries: The serialized nodes, keyed by node key. The function writes the link numbers into them.
        links: The links, each as the `node.output` it starts at and the `node.input` it ends at.

    Returns:
        One record for each link.

    """
    records: list[Json] = []
    for number, (start, end) in enumerate(links, 1):
        # The node key comes first; the rest is the socket's full name, which can name a slot of a growing row.
        source_key, output = start.split('.', 1)
        target_key, input_name = end.split('.', 1)
        origin, target = entries[source_key], entries[target_key]
        origin_slot = find_slot(origin, 'outputs', output)
        target_slot = find_slot(target, 'inputs', input_name)
        cast('list[int]', cast('list[Json]', origin['outputs'])[origin_slot]['links']).append(number)
        cast('list[Json]', target['inputs'])[target_slot]['link'] = number
        kind = cast('list[Json]', origin['outputs'])[origin_slot]['type']
        records.append(
            {
                'id': number,
                'origin_id': origin['id'],
                'origin_slot': origin_slot,
                'target_id': target['id'],
                'target_slot': target_slot,
                'type': kind,
            }
        )
    return records


__all__ = ['encode_links', 'encode_nodes', 'find_slot']
