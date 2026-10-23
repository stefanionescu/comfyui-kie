"""Messages about finding a model on KIE, and whether a node can run it."""

MODEL_EMPTY = "Type a KIE model ID into model, such as {example}. Each model's page on {market} shows its ID."

MODEL_FORM = (
    'The text "{model}" in model is not a KIE model ID. Copy the ID from the model\'s page on {market}, such as '
    '{example}.'
)

MODEL_KIND = 'The model {model} makes {made}, so it runs in {node}, not in {this}.'

MODEL_NO_KIND = 'KIE lists no task type for {model}, so the node cannot tell what it makes.'

MODEL_NO_SCHEMA = (
    'KIE has not published the inputs of {model} yet, so the node cannot check them before paying. Try again later, '
    'or choose another model.'
)

MODEL_OTHER_ROUTE = 'The model {model} runs through another KIE route, {route}, which the KIE nodes do not use.'

MODEL_READ_BUSY = 'KIE asked to wait before more model reads, longer than the request timeout allows. Try again soon.'

MODEL_READ_UNREADABLE = 'KIE sent model details this extension cannot read. Update the extension, or try again later.'

MODEL_UNKNOWN = "KIE has no model with the ID {model}. Copy the ID from the model's page on {market}."

# What each kind of model makes, as the refusals name it.
KIND_NAMES = {'image': 'images', 'video': 'videos', 'audio': 'audio', 'chat': 'chat replies'}

__all__ = [
    'KIND_NAMES',
    'MODEL_EMPTY',
    'MODEL_FORM',
    'MODEL_KIND',
    'MODEL_NO_KIND',
    'MODEL_NO_SCHEMA',
    'MODEL_OTHER_ROUTE',
    'MODEL_READ_BUSY',
    'MODEL_READ_UNREADABLE',
    'MODEL_UNKNOWN',
]
