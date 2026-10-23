import { browserRoutes } from '#web/routes';
import { browserLimits } from '#web/browser';
import { parsePublicError } from '#web/schema';
import { message, type MessageKey } from '#web/text';
import { parseConfiguration, type Configuration } from '#web/settings/schema';

/** ComfyUI's local API client, which the extension builds. */
export type Fetcher = (route: string, options: RequestInit) => Promise<Response>;

// The message for a failed request, by method; every other method saves.
const failureMessages = new Map<string, MessageKey>([
    ['GET', 'settings.readFailed'],
    ['DELETE', 'settings.removeFailed'],
]);

/**
 * Read a settings reply, and turn a failed one into its message.
 *
 * @param response - The local server's reply.
 * @param method - The HTTP method of the request.
 * @returns The validated settings.
 */
async function readReply(response: Response, method: string): Promise<Configuration> {
    let document: unknown;
    try {
        document = await response.json();
    } catch {
        throw new Error(message('settings.unreadableResponse'));
    }
    if (!response.ok) {
        throw new Error(parsePublicError(document) ?? message(failureMessages.get(method) ?? 'settings.saveFailed'));
    }
    return parseConfiguration(document);
}

/**
 * Read or change settings through the local ComfyUI server.
 *
 * @param fetcher - ComfyUI's local API client.
 * @param signal - The settings dialog's request lifetime.
 * @param route - The local settings route.
 * @param method - The HTTP method.
 * @param body - The settings change, if any.
 * @returns The validated settings after the request.
 */
export async function requestConfiguration(
    fetcher: Fetcher,
    signal: AbortSignal,
    route: string = browserRoutes.settings.status,
    method: string = 'GET',
    body?: unknown,
): Promise<Configuration> {
    const options: RequestInit = {
        method,
        cache: 'no-store',
        credentials: 'same-origin',
        signal: AbortSignal.any([signal, AbortSignal.timeout(browserLimits.requestTimeoutMilliseconds)]),
        headers: { 'Content-Type': 'application/json', 'X-KIE-Comfy': '1' },
    };
    if (body !== undefined) options.body = JSON.stringify(body);
    let response: Response;
    try {
        response = await fetcher(route, options);
    } catch {
        throw new Error(message('settings.unreachable'));
    }
    return readReply(response, method);
}
