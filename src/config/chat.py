"""How Chat: Ask writes one request in each of KIE's chat formats, and which settings each format honors.

The live probes of 2026-10-23 and 2026-10-24 found that every format drops temperature, top_p, top_k, and the token
caps, so the node offers none of them.
"""

# The reasoning efforts the node offers, the same as the other chat packs offer; default sends nothing.
EFFORTS = ('default', 'none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max')

# The efforts each format takes. GPT turned minimal into none in the probes, so Responses refuses minimal. Claude's only
# switch, thinkingFlag, changed nothing, so Messages takes none; Chat Completions and native Gemini take low and high.
FORMAT_EFFORTS = {
    'responses': ('none', 'low', 'medium', 'high', 'xhigh', 'max'),
    'messages': (),
    'completions': ('low', 'high'),
    'gemini': ('low', 'high'),
}

# The formats that honor an answer schema. Claude ignored output_config, and native Gemini failed with responseSchema.
SCHEMA_FORMATS = ('responses', 'completions')

# The formats that read a PDF. Claude ignored one in the probes, and native Gemini failed with one.
PDF_FORMATS = ('responses',)

# A PDF goes as a file part; any other document goes as text.
PDF_MEDIA_TYPE = 'application/pdf'

# A text document goes to the model as text, under its name.
DOCUMENT_TEXT = 'Document {name}:\n\n{text}'

# The document files the input folder may hold, with the media type each goes as.
DOCUMENT_TYPES = {
    '.pdf': PDF_MEDIA_TYPE,
    '.txt': 'text/plain',
    '.md': 'text/markdown',
    '.csv': 'text/csv',
    '.json': 'application/json',
}

# The name an answer schema goes under, where the format asks for one.
ANSWER_NAME = 'answer'

# The role each format gives each message. Native Gemini names the model's own turns model.
ROLES = {
    'USER': 'user',
    'ASSISTANT': 'assistant',
    'SYSTEM': 'system',
    'GEMINI_ASSISTANT': 'model',
}

__all__ = [
    'ANSWER_NAME',
    'DOCUMENT_TEXT',
    'DOCUMENT_TYPES',
    'EFFORTS',
    'FORMAT_EFFORTS',
    'PDF_FORMATS',
    'PDF_MEDIA_TYPE',
    'ROLES',
    'SCHEMA_FORMATS',
]
