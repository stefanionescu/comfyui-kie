# Model: Info

Shows what any KIE model takes, as JSON: every input with its type, default,
choices, range, and length limit. Use it to fill the `arguments` of a paid node
and the `field` of **File: Add**. It reads the model from KIE with your API key.
The read is free.

## Inputs

| Input   | What it takes                                                                    |
| ------- | -------------------------------------------------------------------------------- |
| `model` | A model ID, such as `wan/3-0-video`. The model's page on kie.ai/market shows it. |

## Outputs

| Output | What it carries                              |
| ------ | -------------------------------------------- |
| `info` | The model's inputs as JSON, with these keys. |

| Key        | What it holds                                                               |
| ---------- | --------------------------------------------------------------------------- |
| model      | The ID as typed. Paid nodes send exactly this ID.                           |
| title      | KIE's title for the model.                                                  |
| provider   | The company that made the model.                                            |
| task_types | KIE's task types, such as `Text to Video`.                                  |
| kind       | What the model makes: `image`, `video`, `audio`, or `chat`.                 |
| node       | The paid node that runs it, such as `Video: Generate`.                      |
| format     | `job` for image, video, and audio models; the chat format for a chat model. |
| route      | The KIE route the model runs on.                                            |
| inputs     | Every input, with its name, type, default, choices, range, and list size.   |

For example, one input of `wan/3-0-video`:

```json
{
    "field": "reference_audio_urls",
    "type": "array",
    "required": false,
    "default": null,
    "choices": null,
    "minimum": null,
    "maximum": null,
    "list": true,
    "max_items": 5,
    "max_length": null,
    "link": true,
    "description": "Reference audio for the all-purpose reference mode, with up to 5 clips."
}
```

`link` is `true` when KIE marks the input as a file link. `max_length` is the
longest text the input takes, in characters.

## Use

1. Type or connect the model ID.
2. Connect `info` to **Preview as Text** to read it.

An input that takes a file, such as `reference_audio_urls`, gets its files
through **File: Add**. Every other input goes in a named input of the paid node
or in its `arguments`, under its `field` name.

[KIE models](https://kie.ai/market)
