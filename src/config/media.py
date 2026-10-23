"""How the extension encodes ComfyUI media for the KIE upload host, and sorts the files a task makes by kind."""

# A ComfyUI `IMAGE` tensor: batch, height, width, and three or four channels.
IMAGE_TENSOR = {
    'DIMENSIONS': 4,
    'RGB_CHANNELS': 3,
    'RGBA_CHANNELS': 4,
}

# A ComfyUI `MASK`: a batch of height-by-width frames, or one frame alone.
MASK_TENSOR = {
    'DIMENSIONS': 3,
    'FRAME_DIMENSIONS': 2,
}

# What each kind of local media becomes: lossless WebP for images, PNG for masks, 16-bit WAV, and MP4. Contract run C4
# found that KIE's models read lossless WebP.
ENCODED_FORMATS = {
    'image': {'CONTENT_TYPE': 'image/webp', 'EXTENSION': 'webp'},
    'mask': {'CONTENT_TYPE': 'image/png', 'EXTENSION': 'png'},
    'audio': {'CONTENT_TYPE': 'audio/wav', 'EXTENSION': 'wav'},
    'video': {'CONTENT_TYPE': 'video/mp4', 'EXTENSION': 'mp4'},
}

# Lossless WebP keeps the pixels of a PNG in about a third less space. Method 1 encodes fast, and exact keeps the
# colors under fully clear pixels.
WEBP = {'METHOD': 1, 'QUALITY': 0}

# The WAV container and codec that PyAV writes audio with.
WAV = {
    'FORMAT': 'wav',
    'CODEC': 'pcm_s16le',
}

# An upload's file name holds its kind and the start of its SHA-256 digest.
DIGEST_CHARACTERS = 12

# The kind of a file a task made, by the extension of its link. Any other file stays a link.
OUTPUT_EXTENSIONS = {
    '.png': 'image',
    '.jpg': 'image',
    '.jpeg': 'image',
    '.webp': 'image',
    '.gif': 'image',
    '.bmp': 'image',
    '.mp4': 'video',
    '.mov': 'video',
    '.webm': 'video',
    '.mp3': 'audio',
    '.wav': 'audio',
    '.flac': 'audio',
    '.ogg': 'audio',
    '.m4a': 'audio',
    '.aac': 'audio',
}

# The node outputs that hold decoded files, and the kind of file each decodes; masks come from the images.
OUTPUT_ID_KINDS = {
    'images': 'image',
    'masks': 'image',
    'video': 'video',
    'audio': 'audio',
}

# The only scheme a link may have; KIE reads public https links.
LINK_SCHEME = 'https'

# A typical web address limit; longer text is a paste mistake.
MAX_LINK_CHARACTERS = 2048

__all__ = [
    'DIGEST_CHARACTERS',
    'ENCODED_FORMATS',
    'IMAGE_TENSOR',
    'LINK_SCHEME',
    'MASK_TENSOR',
    'MAX_LINK_CHARACTERS',
    'OUTPUT_EXTENSIONS',
    'OUTPUT_ID_KINDS',
    'WAV',
    'WEBP',
]
