# KIE Advanced Guide

Use this guide for model settings, chat capabilities, media, and task recovery.
For installation, see the [README](README.md). Node help covers
[individual inputs and outputs](README.md#nodes).

## Keys and access

Save your API key in **Extensions > KIE > KIE Settings** from the
ComfyUI menu. The key stays on the server and out of saved workflows.
`KIE_API_KEY`, set where ComfyUI starts, overrides the saved key.

Only a direct local, single-user connection can change the key or settings.
For remote access, a reverse proxy, or multi-user mode, set `KIE_API_KEY`
on the ComfyUI server and restart it.

The extension stores settings, credentials, and task records in this private folder:

| System  | Folder                                        |
| ------- | --------------------------------------------- |
| macOS   | `~/Library/Application Support/KIEComfyUI`    |
| Linux   | `${XDG_STATE_HOME:-~/.local/state}/kie-comfy` |
| Windows | `%LOCALAPPDATA%\KIEComfyUI`                   |

Set `KIE_COMFY_STATE_DIRECTORY` to use another absolute path outside
the extension and ComfyUI's folders. The extension writes unencrypted files with owner-only permissions.

## Settings

Change limits in **KIE Settings**. New requests use the saved values;
changing settings does not cancel active work. Model limits also apply.

| Setting                        | Default | Range      | What it limits                                                        |
| ------------------------------ | ------- | ---------- | --------------------------------------------------------------------- |
| **Request timeout (seconds)**  | 1800    | 10 to 3600 | How long one request may take, and the whole wait for a task.         |
| **Maximum upload size (MB)**   | 100     | 1 to 100   | Each image, mask, audio clip, video, or document the extension sends. |
| **Maximum download size (MB)** | 512     | 16 to 4096 | The largest reply or output file the extension accepts.               |

## Models

Use the exact ID from [KIE's model catalog](https://kie.ai/market). KIE must
publish an input schema, and the model must return the output kind of the node.
An upscaler or background remover uses **Image: Generate**.

| Node            | Runs models that make | Default model                          |
| --------------- | --------------------- | -------------------------------------- |
| Image: Generate | Images                | `gpt-image-2-5-sunburst-text-to-image` |
| Video: Generate | Video                 | `wan/3-0-video`                        |
| Audio: Generate | Audio                 | `elevenlabs/text-to-speech-turbo-2-5`  |
| Chat: Ask       | Chat replies          | `gpt-6-luna`                           |

**Model: Info** lists the model's inputs, choices, and defaults. The extension
reads each schema once per ComfyUI session. It rejects unknown input names;
KIE can otherwise ignore an unknown field while still running a paid task.

Use named inputs for common settings. Empty text or `default` sends no value;
`custom` sends the chosen number. Other settings go in `arguments` as a JSON
object using KIE's exact input names and value types, such as `{"audio": false}`.
Do not set the same field in both places.

Omitted inputs use KIE's defaults. Check resolution, duration, and output count
before running because these can affect cost. KIE checks submitted values.

## Chat models

KIE serves its chat models in four request formats, and the schema of each
model names its format. GPT uses OpenAI Responses, Claude uses Anthropic
Messages, and Gemini uses native Gemini or Chat Completions. **Chat: Ask**
writes the question in that format: the system prompt, the earlier turns, the
documents, the images, then the prompt.

KIE drops `temperature`, `top_p`, `top_k`, and the token limits on every
format, so the node offers none of them. It takes only what KIE honors:

| Input              | GPT                                             | Claude | Gemini        |
| ------------------ | ----------------------------------------------- | ------ | ------------- |
| `reasoning_effort` | `none`, `low`, `medium`, `high`, `xhigh`, `max` | none   | `low`, `high` |
| `json_schema`      | Yes, as the `json_schema` text format           | No     | No            |
| PDF documents      | Yes                                             | No     | No            |
| Text documents     | Yes                                             | Yes    | Yes           |
| `system_prompt`    | Yes                                             | Yes    | Yes           |

`extra_fields` adds other fields to the request as written, in the format of
the model. The node refuses a field it sets itself.

## Files and uploads

Use **File: Add** to connect media to a model input. Set `field` to its exact
name, such as `image_urls` or `reference_audio_urls`. `file` accepts an HTTPS
link, the `files` output of another KIE node, or local ComfyUI image, mask, audio, or video.
Chain **File: Add** nodes and connect the final `files` to the generation node.
Files keep chain order; list inputs receive a list even for one file.

The extension uploads local images as lossless WebP, masks as PNG, audio as
WAV, and video as MP4. It reuses existing KIE output links without uploading.
Uploads last 24 hours; generated files last 14 days. Anyone with a file link
can open it. Save outputs locally before their links expire.

**Chat: Attach Document** reads PDF or UTF-8 text files from ComfyUI's input
folder. Chat returns the answer, available reasoning, and conversation.
Generation nodes return media, file links, and the provider's JSON in `result`.

## Caching and reruns

Change `run_number` to request another generation with unchanged inputs.
Use a custom `seed` to send one; otherwise the model chooses its default.
A different effective key invalidates cached results; changing limits does not.
Every request uploads its own local files. The node reuses connected output links.

## Recover a task

KIE cannot cancel an accepted task. It continues after cancellation in ComfyUI,
a restart, or a timeout, and can incur charges. The extension records accepted
tasks and does not submit them again automatically.

Use **Task: Download** and press R to refresh the list. Records leave the list
after download, when KIE drops them, or after 14 days. Recover an existing task
before submitting another paid generation.

## Troubleshooting

| Symptom                                | Action                                                                                 |
| -------------------------------------- | -------------------------------------------------------------------------------------- |
| The key is rejected                    | Check it at [API keys](https://kie.ai/api-key); `KIE_API_KEY` overrides the saved key. |
| Credits are insufficient               | Check the account's [billing page](https://kie.ai/billing).                            |
| A model or schema is missing           | Copy the catalog ID and inspect it with **Model: Info**.                               |
| An input name is unsupported           | Clear its named setting and use the model's actual input name in `arguments`.          |
| Chat rejects reasoning, JSON, or a PDF | Check the [chat capability table](#chat-models).                                       |
| Requests are rate-limited              | Wait before another run. The extension spaces its own catalog reads.                   |
| A video has not arrived                | Recover its task with **Task: Download**.                                              |
| Settings cannot be changed             | Connect directly from localhost; use `KIE_API_KEY` for remote or multi-user access.    |

For an unknown setting or an oversized state file:

Stop ComfyUI and back up the affected file in the private state folder.
To reset limits, remove only `settings.json`, then restart. Keep task records
until you have recovered their outputs. Do not delete the whole state folder
to reset a setting.

## Update or remove

To update, replace `custom_nodes/kie` and restart
ComfyUI. Open updated examples in a new tab.

To remove the extension, move its folder outside `custom_nodes` and restart.
Private state and saved media remain. Back up state and recover outstanding
tasks before deleting the private folder: that removes the saved key,
settings, and task records. Removing a saved key does not revoke it with the provider.
