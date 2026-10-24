import '#web/interface.css';
import { message } from '#web/text';
import { api } from '../../scripts/api.js';
import { app } from '../../scripts/app.js';
import { openSettings } from '#web/settings/dialog';
import { refreshGraph, addNodeControls } from '#web/controls';

/**
 * Read the language ComfyUI shows, which the server's messages follow.
 *
 * @returns A valid language tag, or English when the setting is invalid.
 */
function selectLocale(): string {
    const value = app.extensionManager.setting.get('Comfy.Locale');
    try {
        return Intl.getCanonicalLocales(typeof value === 'string' ? value.replaceAll('_', '-') : 'en')[0] ?? 'en';
    } catch {
        return 'en';
    }
}

/**
 * Send a local request through ComfyUI, in the language ComfyUI shows.
 *
 * @param route - The path of the local settings route.
 * @param options - The request's method, headers, and body.
 * @returns The local ComfyUI response.
 */
function requestLocal(route: string, options: RequestInit): Promise<Response> {
    const headers = new Headers(options.headers);
    headers.set('Accept-Language', selectLocale());
    return api.fetchApi(route, { ...options, headers });
}

app.registerExtension({
    name: 'KIE',
    setup: () => {
        const stylesheet = document.createElement('link');
        stylesheet.rel = 'stylesheet';
        stylesheet.href = new URL('extension.css', import.meta.url).href;
        const stylesheets = new Set();
        for (const link of document.querySelectorAll('link[rel=stylesheet]')) {
            stylesheets.add(link.getAttribute('href'));
        }
        if (!stylesheets.has(stylesheet.href)) document.head.append(stylesheet);
    },
    nodeCreated: (canvasNode) => {
        addNodeControls(app, canvasNode);
    },
    afterConfigureGraph: () => {
        refreshGraph(app);
    },
    commands: [
        {
            id: 'KIE.OpenSettings',
            label: message('settings.menu'),
            function: openSettings.bind(null, requestLocal),
        },
    ],
    menuCommands: [
        {
            path: ['Extensions', 'KIE'],
            commands: ['KIE.OpenSettings'],
        },
    ],
});
