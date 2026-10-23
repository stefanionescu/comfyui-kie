"""Messages for media that the extension cannot encode, upload, or read."""

AUDIO_EMPTY = 'The connected audio has no samples.'

AUDIO_UNREADABLE = 'An audio file that KIE returned could not be decoded.'

AUDIO_UNWRITABLE = 'The connected audio could not be written as WAV. Use mono or stereo audio.'

IMAGE_CHANNELS = 'Connect a ComfyUI image with three or four color channels.'

IMAGE_PIXELS = 'The connected image or mask holds values that are not numbers. Check the node that made it.'

IMAGE_UNREADABLE = 'An image that KIE returned could not be decoded.'

MASK_SHAPE = 'Connect a ComfyUI mask: one value for each pixel, with no color channels.'

UPLOAD_FAILED = 'The KIE upload host refused a file: {reason}'

UPLOAD_LIMIT = (
    'A connected file is {size} MB, above the maximum upload size of {maximum} MB in KIE Settings. Raise the limit, '
    'or put the file at a public link and add it with File: Add.'
)

VIDEO_UNREADABLE = 'A video that KIE returned could not be read.'

VIDEO_UNWRITABLE = 'The connected video could not be written as MP4.'

__all__ = [
    'AUDIO_EMPTY',
    'AUDIO_UNREADABLE',
    'AUDIO_UNWRITABLE',
    'IMAGE_CHANNELS',
    'IMAGE_PIXELS',
    'IMAGE_UNREADABLE',
    'MASK_SHAPE',
    'UPLOAD_FAILED',
    'UPLOAD_LIMIT',
    'VIDEO_UNREADABLE',
    'VIDEO_UNWRITABLE',
]
