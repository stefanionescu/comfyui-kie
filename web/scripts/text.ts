/** The text the extension's dialogs show, addressed by dotted key. */
const TEXT = {
    close: 'Close',
    settings: {
        clearKey: 'Clear Saved Key',
        close: 'Close KIE Settings',
        credentialLabel: 'KIE API key',
        credentials: 'Credentials',
        environmentKey: 'Set by KIE_API_KEY',
        invalidDefinition: 'ComfyUI returned an invalid KIE setting definition.',
        invalidLimit: 'ComfyUI returned an invalid KIE limit.',
        invalidResponse: 'ComfyUI returned an invalid KIE settings response.',
        keyCleared: 'Saved key cleared.',
        keyNotice:
            'Add a KIE API key to use the extension. Your key stays on your ComfyUI server and is sent only to KIE.',
        keySaved: 'Key saved.',
        limits: 'Request limits',
        limitsSaved: 'Limits saved.',
        reread: 'Settings loaded.',
        reading: 'Loading settings...',
        noLimitChanges: 'No limit changes to save.',
        readOnly: "Changes are disabled in this host's multi-user mode.",
        reload: 'Reload Settings',
        saveFailed: 'ComfyUI could not save the KIE settings.',
        saveKey: 'Save Key',
        saveLimits: 'Save Limits',
        savedKey: 'Saved key',
        title: 'KIE Settings',
        unreachable: 'Cannot reach the KIE settings. Check ComfyUI and try again.',
        unreadableResponse: 'ComfyUI returned an unreadable KIE settings response.',
        updateFailed: 'The KIE settings could not be saved.',
        readFailed: 'ComfyUI could not read the KIE settings.',
        removeFailed: 'ComfyUI could not clear the saved KIE API key.',
        menu: 'KIE Settings',
    },
    working: 'Working...',
} as const;

/** Labels of the server's execution limits, keyed by setting name. */
export const LIMIT_LABELS = new Map<string, string>([
    ['max_download_megabytes', 'Maximum download size (MB)'],
    ['max_upload_megabytes', 'Maximum upload size (MB)'],
    ['request_timeout_seconds', 'Request timeout (seconds)'],
]);

type MessagePaths<Messages> = {
    [Key in keyof Messages & string]: Messages[Key] extends string ? Key : `${Key}.${MessagePaths<Messages[Key]>}`;
}[keyof Messages & string];

export type MessageKey = MessagePaths<typeof TEXT>;

/**
 * Read one message.
 *
 * @param key - A dotted path into the extension's text.
 * @returns The text at that path.
 */
export function message(key: MessageKey): string {
    let value: unknown = TEXT;
    for (const part of key.split('.')) {
        value = (value as Record<string, unknown>)[part];
    }
    return String(value);
}
