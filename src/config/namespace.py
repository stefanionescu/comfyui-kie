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

__all__ = ['MENUS', 'NODE_PREFIX']
