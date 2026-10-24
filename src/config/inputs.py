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
    'MODEL': 'Any KIE model ID, such as wan/3-0-video. Copy one from its page on kie.ai/market.',
    'RUN_NUMBER': 'Change this number to send the same request again.',
    'ARGUMENTS': (
        'The model\'s other inputs as a JSON object, under the names Model: Info lists, such as {"resolution": '
        '"480p"}. Leave it empty to use the model\'s defaults.'
    ),
    'aspect_ratio': 'The shape of the result, such as 16:9. Choose custom to send one.',
    'resolution': 'The size of the result, such as 1K or 720p. Choose custom to send one.',
    'output_format': 'The file format of the result, such as png. Choose custom to send one.',
    'seed': 'Number the model uses to vary its output. Choose custom to send one.',
    'duration': 'The length in seconds. Choose custom to send one.',
    'prompt': (
        "Sent as the model's prompt input. Leave it empty when the model has none or takes its text under another "
        'name, and put that text in arguments.'
    ),
    'negative_prompt': 'What to leave out. Leave it empty to send nothing.',
    'text': 'The words to speak, for a voice model. Leave it empty to send nothing.',
    'voice': 'The voice ID, for a voice model. Leave it empty to send nothing.',
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
