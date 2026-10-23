"""Messages for failed requests to KIE; the reason in each is KIE's own, cleaned, and ends as a sentence."""

CREDITS_LOW = 'Your KIE account has too few credits for this request. Add credits at {billing}, then run again.'

DOWNLOAD_LIMIT = 'The reply is larger than {maximum} MB. Raise the maximum download size in KIE Settings.'

GENERATION_FAILED = 'The model could not make a result: {reason} Change the prompt or the inputs, then run again.'

KEY_LIMIT = 'This API key reached a limit set on it. Raise the limit at {keys}, or use another key.'

KEY_REJECTED = 'KIE refused the API key. Check it at {keys}, then save it again in KIE Settings.'

KIE_UNREACHABLE = 'ComfyUI could not reach KIE. Check the internet connection, then run again.'

MAINTENANCE = 'KIE is down for maintenance. Run again later.'

NO_REASON = 'KIE gave no reason.'

NOT_FOUND = 'KIE does not know what this request names: {reason}'

RATE_LIMITED = 'KIE got too many requests from this account. Wait a few seconds, then run again.'

READ_TIMEOUT = 'KIE did not answer within {seconds} seconds. Run again, or raise the request timeout in KIE Settings.'

REPLY_UNREADABLE = 'KIE sent a reply this extension cannot read. Update the extension, or try again later.'

REQUEST_REJECTED = 'KIE refused the request: {reason} Change what it names, then run again.'

RESULT_LATE = 'The model made no result for over 10 minutes: {reason} Run again later.'

SERVER_FAILED = 'KIE did not run the request: {reason} Fix what it names, or run again in a minute.'

SWITCHED_OFF = 'KIE has switched off what this request uses: {reason}'

__all__ = [
    'CREDITS_LOW',
    'DOWNLOAD_LIMIT',
    'GENERATION_FAILED',
    'KEY_LIMIT',
    'KEY_REJECTED',
    'KIE_UNREACHABLE',
    'MAINTENANCE',
    'NOT_FOUND',
    'NO_REASON',
    'RATE_LIMITED',
    'READ_TIMEOUT',
    'REPLY_UNREADABLE',
    'REQUEST_REJECTED',
    'RESULT_LATE',
    'SERVER_FAILED',
    'SWITCHED_OFF',
]
