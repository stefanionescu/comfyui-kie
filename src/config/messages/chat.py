"""Refusals of Chat: Ask, which come before it pays for anything."""

CHAT_FIELD_TWICE = 'Chat: Ask sets {field} itself for {model}. Remove {field} from extra_fields.'

CHAT_REPLY_EMPTY = 'The model {model} sent no text. Run again, or try another model.'

DOCUMENT_KIND = 'Choose a PDF, text, Markdown, CSV, or JSON document.'

DOCUMENT_MISSING = "Put a PDF or text file in ComfyUI's input folder, press R, and choose it."

DOCUMENT_OUTSIDE = "Choose a document inside ComfyUI's input folder."

DOCUMENT_SIZE = 'The document is larger than {maximum} MB, the maximum upload size in KIE Settings.'

DOCUMENT_UNREADABLE = 'The document could not be read as UTF-8 text. Save it as UTF-8 or as a PDF.'

JSON_SCHEMA_INVALID = 'Write json_schema as a JSON object with a name and a schema.'

EFFORT_REFUSED = 'The model {model} takes the reasoning efforts {efforts}. Choose one of them, or default.'

EFFORT_NOT_TAKEN = 'KIE runs {model} with no reasoning effort. Set reasoning_effort to default.'

PDF_REFUSED = (
    'KIE sends PDFs only to GPT models, and {model} does not read them. Choose a GPT model, or attach the text as a '
    'text file.'
)

PROMPT_EMPTY = 'Write a prompt for the model.'

SCHEMA_REFUSED = (
    'KIE runs {model} without a JSON schema for the answer, so json_schema would change nothing. Clear it, or choose a '
    'GPT model.'
)

__all__ = [
    'CHAT_FIELD_TWICE',
    'CHAT_REPLY_EMPTY',
    'DOCUMENT_KIND',
    'DOCUMENT_MISSING',
    'DOCUMENT_OUTSIDE',
    'DOCUMENT_SIZE',
    'DOCUMENT_UNREADABLE',
    'EFFORT_NOT_TAKEN',
    'EFFORT_REFUSED',
    'JSON_SCHEMA_INVALID',
    'PDF_REFUSED',
    'PROMPT_EMPTY',
    'SCHEMA_REFUSED',
]
