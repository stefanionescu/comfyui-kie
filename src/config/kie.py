"""KIE's hosts and routes, the replies the extension reads from them, and the pages its messages name."""

# Every request that carries the API key goes to one of these hosts: the API, and the host that takes uploads.
HOSTS = {
    'API': 'api.kie.ai',
    'UPLOAD': 'kieai.redpandaai.co',
}

# KIE's routes: the upload route on the upload host, and the rest on the API host.
ROUTES = {
    'MODELS': '/api/v1/models',
    'SCHEMA': '/api/v1/models/{model}/schema',
    'CREATE_TASK': '/api/v1/jobs/createTask',
    'RECORD_INFO': '/api/v1/jobs/recordInfo',
    'UPLOAD': '/api/file-stream-upload',
}

# The extension reads reply bodies in chunks of this size.
REPLY_BYTES = {
    'CHUNK': 65_536,
}

# The code in the body of a reply that succeeded. KIE answers most failures with HTTP 200 and another code here.
SUCCESS_CODE = 200

# The extension cuts a reason from KIE to this many characters, and ends it as a sentence.
MAX_REASON_CHARACTERS = 300
REASON_ENDINGS = ('.', '!', '?', '…')

# KIE's pages that messages send people to, written without the scheme.
PAGES = {
    'KEYS': 'kie.ai/api-key',
    'BILLING': 'kie.ai/billing',
    'LOGS': 'kie.ai/logs',
    'MARKET': 'kie.ai/market',
}

__all__ = [
    'HOSTS',
    'MAX_REASON_CHARACTERS',
    'PAGES',
    'REASON_ENDINGS',
    'REPLY_BYTES',
    'ROUTES',
    'SUCCESS_CODE',
]
