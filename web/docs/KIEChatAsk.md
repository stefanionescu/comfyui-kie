# Chat: Ask

Asks a KIE chat model a question. Images and documents go along when the
model reads them. Returns the answer, the reasoning of the model, and the
conversation so far.

## Inputs

| Input              | What it takes                                                                                                                                                  |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`            | Any chat model ID from kie.ai/market; the default is `gpt-6-luna`.                                                                                             |
| `conversation`     | Earlier turns, from another **Chat: Ask**.                                                                                                                     |
| `documents`        | Files from **Chat: Attach Document**. PDFs need a GPT model; text files go to any model.                                                                       |
| `images`           | Images: one, a batch, or a list. Each goes as lossless WebP at its own size.                                                                                   |
| `reasoning_effort` | How much the model thinks: `none`, `low`, `medium`, `high`, `xhigh`, or `max` for GPT models, and `low` or `high` for Gemini models.                           |
| `run_number`       | Change this number to send the same request again.                                                                                                             |
| `json_schema`      | For GPT models, the `json_schema` format object: a `name` and the `schema` the answer must follow, with `strict` if you want it. Leave it empty for free text. |
| `prompt`           | The question or instruction.                                                                                                                                   |
| `system_prompt`    | The system prompt: instructions for the whole answer.                                                                                                          |
| `extra_fields`     | Other request fields as a JSON object, in the format of the model, added to the request as written.                                                            |

## Outputs

| Output         | What it carries                                                                |
| -------------- | ------------------------------------------------------------------------------ |
| `text`         | The answer.                                                                    |
| `reasoning`    | The reasoning the model shows. Connected nodes are skipped when there is none. |
| `conversation` | The earlier turns plus this question and answer, for the next **Chat: Ask**.   |

## Use

1. Write the prompt and type the model ID.
2. Connect any images or documents the model reads.
3. Connect `text` to **Preview as Text**, and select **Run**.

Everything connected goes in one request. To ask about the same images in a
later turn, connect them again.

KIE serves GPT, Claude, and Gemini models, each in its own request format, and
drops temperature, top_p, top_k, and token limits on all of them, so the node
offers none.

Before it pays, the node refuses a `reasoning_effort` or a `json_schema` that
the model does not take. It also refuses a PDF for a model other than GPT, and
a field in `extra_fields` that the node sets itself.

[KIE chat models](https://kie.ai/market)
