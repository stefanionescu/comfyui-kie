"""The names this extension uses in spaces it shares with other packs."""

# Every node ID is this prefix and the class name, such as KIEModelInfo.
NODE_PREFIX = 'KIE'

# The menus that group the nodes, in KIE's own spelling.
MENUS = {
    'SHARED': 'KIE',
    'IMAGE': 'KIE/Image',
    'VIDEO': 'KIE/Video',
    'AUDIO': 'KIE/Audio',
    'CHAT': 'KIE/Chat',
}

# The socket types more than one node shares, prefixed so no other pack's socket of the same name connects.
SOCKET_TYPES = {
    'FILES': 'KIE_FILES',
    'CONVERSATION': 'KIE_CONVERSATION',
    'DOCUMENTS': 'KIE_DOCUMENTS',
}

__all__ = ['MENUS', 'NODE_PREFIX', 'SOCKET_TYPES']
