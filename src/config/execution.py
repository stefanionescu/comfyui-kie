"""How a node notices ComfyUI's cancel while it waits for KIE."""

# How often a wait checks ComfyUI's cancel, in seconds.
CANCELLATION_POLL_SECONDS = 0.1

__all__ = ['CANCELLATION_POLL_SECONDS']
