# Image: Generate

Runs any KIE model that makes images: generating, editing, upscaling, and
removing backgrounds. It outputs the images, a mask for each, and the link of
every file the model made.

## Inputs

| Input             | What it takes                                                                                   |
| ----------------- | ----------------------------------------------------------------------------------------------- |
| `files`           | Input images from **File: Add**, each under the input name of the model, such as `image_urls`.  |
| `model`           | The model ID, such as `nano-banana-pro`. The default is `gpt-image-2-5-sunburst-text-to-image`. |
| `aspect_ratio`    | `default`, or `custom` and a shape, such as `16:9`.                                             |
| `resolution`      | `default`, or `custom` and a size, such as `2K`.                                                |
| `output_format`   | `default`, or `custom` and a file type, such as `png`.                                          |
| `seed`            | `default`, or `custom` and a number. The same seed repeats a result.                            |
| `run_number`      | Change this number to send the same request again.                                              |
| `prompt`          | The text sent as the model's `prompt`. Leave it empty for a model without one.                  |
| `negative_prompt` | What to leave out, for a model that takes it. Empty sends nothing.                              |
| `arguments`       | The model's other inputs as JSON, under KIE's names, such as `{"background": "opaque"}`.        |

Each setting at `default` sends nothing, so the model uses its own default. A
setting at `custom` goes under its own name, and only a model with an input of
that name takes it. A model that names it another way, such as `size` or
`image_size`, takes it in `arguments`. **Model: Info** lists the inputs and
choices of a model. The node checks the model and its inputs before it pays.

## Outputs

| Output   | What it carries                                                                               |
| -------- | --------------------------------------------------------------------------------------------- |
| `images` | Every image, each at its own size, in the order KIE returned them.                            |
| `masks`  | One mask per image, from its transparency. White is transparent; opaque images are all black. |
| `files`  | The link of every file the model made, for the next KIE node.                                 |
| `result` | The whole result from KIE, as JSON.                                                           |

## Use

1. Type the model ID in `model`, and write the prompt.
2. Set `aspect_ratio`, `resolution`, or other settings to `custom` where the
   model takes them.
3. To edit an image, connect **File: Add** with the image input of the model,
   such as `image_urls`, to `files`.
4. Connect `images` to **Save Image**, and select **Run**.

[KIE image models](https://kie.ai/market)
