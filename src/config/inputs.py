"""Names, tooltips, and ranges of the inputs the nodes share, and the named settings of each paid node."""

# The inputs that several nodes share.
INPUT_NAMES = {
    'FILES': 'files',
    'MODEL': 'model',
    'RUN_NUMBER': 'run_number',
    'ARGUMENTS': 'arguments',
}

# The run number's default and range; changing it sends the same request again.
RUN_NUMBER = {'DEFAULT': 0, 'MIN': 0, 'MAX': 2**31 - 1}

# The choices of a named setting: default sends nothing, and custom shows a value, which the node sends.
CHOICE = {
    'DEFAULT': 'default',
    'CUSTOM': 'custom',
    'VALUE': 'value',
}

# The named settings of each job node, in node order, by KIE's input name, with the value custom starts at. Each runs
# only on a model that has an input of that name; Model: Info shows the values a model takes.
SETTINGS: dict[str, dict[str, str | int]] = {
    'image': {'aspect_ratio': '1:1', 'resolution': '1K', 'output_format': 'png', 'seed': 42},
    'video': {'duration': 5, 'resolution': '720p', 'aspect_ratio': '16:9', 'seed': 42},
    'audio': {},
}

# The range of each named setting that takes a number.
NUMBER_RANGES = {
    'duration': (1, 120),
    'seed': (0, 2**31 - 1),
}

# The one-line text inputs of each job node, by KIE's input name, with the text they start with. They come first among
# the text inputs. The voice starts at the voice that the schema of the default audio model gives: James, on ElevenLabs.
LINES: dict[str, dict[str, str]] = {
    'image': {},
    'video': {},
    'audio': {'voice': 'EkK5I93UQWFDigLMpZcX'},
}

# The text boxes of each job node, in node order, by KIE's input name.
TEXTS = {
    'image': ('prompt', 'negative_prompt'),
    'video': ('prompt', 'negative_prompt'),
    'audio': ('prompt', 'text'),
}

# Tooltips of the shared inputs, the named settings, and the text boxes, in plain words.
TOOLTIPS = {
    'FILES': 'Files for the model, each for the input its File: Add names.',
    'MODEL': "The KIE model to run: its model ID, such as wan/3-0-video. Each model's page on kie.ai/market shows it.",
    'RUN_NUMBER': 'Change it to send the same request again.',
    'ARGUMENTS': (
        'Other inputs of the model as a JSON object, under the names Model: Info lists, such as {"background": '
        '"opaque"}. Leave it empty to use the defaults of the model.'
    ),
    'aspect_ratio': 'The shape of the result, such as 16:9. Choose custom to set it.',
    'resolution': 'The size of the result, such as 1K or 720p. Choose custom to set it.',
    'output_format': 'The file type of the result, such as png. Choose custom to set it.',
    'seed': 'The number the model starts from; the same seed repeats a result. Choose custom to set it.',
    'duration': 'The length of the video, in seconds. Choose custom to set it.',
    'prompt': 'What to make. Sent as the input named prompt.',
    'negative_prompt': 'What to leave out. Sent as the input named negative_prompt; leave it empty to send nothing.',
    'text': 'The words to speak, for a voice model. Sent as the input named text; leave it empty to send nothing.',
    'voice': 'The voice ID, for a voice model. Sent as the input named voice; leave it empty to send nothing.',
}

__all__ = [
    'CHOICE',
    'INPUT_NAMES',
    'LINES',
    'NUMBER_RANGES',
    'RUN_NUMBER',
    'SETTINGS',
    'TEXTS',
    'TOOLTIPS',
]
