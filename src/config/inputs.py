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

# The choices of a number setting: default sends nothing, and custom shows a value, which the node sends.
CHOICE = {
    'DEFAULT': 'default',
    'CUSTOM': 'custom',
    'VALUE': 'value',
}

# The choices of an on/off setting: default sends nothing, and true or false sends that value.
SWITCH = {
    'DEFAULT': 'default',
    'ON': 'true',
    'OFF': 'false',
}

# The named settings of each job node, by KIE's input name: the inputs most models of the kind share, the same in the
# fal pack. Each runs only on a model that has an input of that name; Model: Info shows the values a model takes. The
# node shows the text settings first, then the on/off settings, then the number settings.

# The text settings of each job node, in node order; each is one line that sends nothing while empty.
TEXT_SETTINGS = {
    'image': ('aspect_ratio', 'resolution', 'output_format'),
    'video': ('resolution', 'aspect_ratio'),
    'audio': ('output_format',),
}

# The on/off settings of each job node, in node order.
SWITCH_SETTINGS = {
    'image': (),
    'video': ('generate_audio',),
    'audio': (),
}

# The number settings of each job node, in node order, with the value custom starts at.
NUMBER_SETTINGS: dict[str, dict[str, int | float]] = {
    'image': {'num_images': 1, 'guidance_scale': 3.5, 'num_inference_steps': 28, 'seed': 42},
    'video': {'duration': 5, 'seed': 42},
    'audio': {'seed': 42},
}

# The least value of each number setting; KIE checks the range of each model itself, free.
NUMBER_MINIMUMS = {
    'num_images': 1,
    'guidance_scale': 0.0,
    'num_inference_steps': 1,
    'duration': 1,
    'seed': 0,
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
    'aspect_ratio': "The shape of the result, such as 16:9. Leave it empty to use the model's default.",
    'resolution': "The size of the result, such as 1K or 720p. Leave it empty to use the model's default.",
    'num_images': 'How many images to make. Choose custom to send a number.',
    'output_format': "The file format of the result, such as png. Leave it empty to use the model's default.",
    'guidance_scale': 'How closely the image follows the prompt; higher follows it more. Choose custom to send one.',
    'num_inference_steps': (
        'How many steps the model takes; more is slower and often finer. Choose custom to send a number.'
    ),
    'seed': 'Number the model uses to vary its output. Choose custom to send one.',
    'duration': 'The length in seconds. Choose custom to send one.',
    'generate_audio': 'Whether the video has sound. At default, the model decides.',
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
    'NUMBER_MINIMUMS',
    'NUMBER_SETTINGS',
    'RUN_NUMBER',
    'SWITCH',
    'SWITCH_SETTINGS',
    'TEXTS',
    'TEXT_SETTINGS',
    'TOOLTIPS',
]
