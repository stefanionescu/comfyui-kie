"""Refusals of the inputs of a paid node, which come before the node uploads or pays for anything."""

ARGUMENTS_INVALID = 'The arguments input is not valid JSON. Write a JSON object, such as {{"resolution": "720p"}}.'

ARGUMENTS_SHAPE = (
    'The arguments input holds {shape}. Write a JSON object of input names and values, such as {{"resolution": '
    '"720p"}}.'
)

ARGUMENT_UNKNOWN = (
    'The model {model} has no input named {field}. KIE would ignore it and still bill the task. Model: Info lists '
    'the inputs the model takes.'
)

FIELD_NOT_FILE = 'The {field} input of {model} takes no file link. Set it in arguments instead.'

FIELD_ONE_FILE = 'The {field} input takes one file, and it has {count}. Keep one.'

FIELD_REQUIRED = 'Set {field}: the model {model} needs it. Model: Info shows what it takes.'

FIELD_TOO_MANY = 'The {field} input of {model} takes at most {maximum} files, and it has {count}. Remove {extra}.'

FIELD_TWICE = 'The {field} input is set twice, in arguments and by {source}. Remove it from one of them.'

FILE_EMPTY = (
    'Connect an image, a mask, audio, a video, or the files of a KIE node to File: Add, or type a link into file.'
)

FILE_FIELD_EMPTY = "Type the model's input into field, such as image_urls. Model: Info lists the inputs of a model."

FILE_FIELD_MISSING = 'Connect files through File: Add, which names the input each file goes to.'

FILE_FIELD_NAME = 'Type one input name into field, such as image_urls: letters, digits, and underscores.'

FILE_FIELD_UNKNOWN = (
    'The model {model} has no input named {field}. Change field on that File: Add; Model: Info lists the inputs the '
    'model takes.'
)

FILE_LINK = 'Type a public https:// link into file, or connect the file instead.'

FILE_LINK_LENGTH = 'Use a link of at most {maximum} characters in file.'

SETTING_UNKNOWN = (
    'The model {model} has no input named {field}. Set {field} to default, and put the setting in arguments under the '
    "model's own name. Model: Info lists its inputs."
)

SINGLE_VALUE = 'Connect one value to {name}, not a list.'

TEXT_UNUSED = (
    'The model {model} takes no {field}. Leave {field} empty, and put the text in arguments under one of its text '
    'inputs: {fields}.'
)

TEXT_NOT_TAKEN = 'The model {model} takes no {field}. Leave {field} empty.'

# How a refusal names a JSON value that is not an object.
JSON_SHAPES = {
    'array': 'a JSON list',
    'string': 'text in double quotes',
    'number': 'a number',
    'boolean': 'true or false',
    'null': 'null',
}

__all__ = [
    'ARGUMENTS_INVALID',
    'ARGUMENTS_SHAPE',
    'ARGUMENT_UNKNOWN',
    'FIELD_NOT_FILE',
    'FIELD_ONE_FILE',
    'FIELD_REQUIRED',
    'FIELD_TOO_MANY',
    'FIELD_TWICE',
    'FILE_EMPTY',
    'FILE_FIELD_EMPTY',
    'FILE_FIELD_MISSING',
    'FILE_FIELD_NAME',
    'FILE_FIELD_UNKNOWN',
    'FILE_LINK',
    'FILE_LINK_LENGTH',
    'JSON_SHAPES',
    'SETTING_UNKNOWN',
    'SINGLE_VALUE',
    'TEXT_NOT_TAKEN',
    'TEXT_UNUSED',
]
