# Video: Generate

Runs any KIE model that makes a video: from text, from a first frame, from
reference images, video, and voice clips, and lip sync and upscaling. It
outputs the video and the link of every file the model made.

## Inputs

| Input             | What it takes                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------------ |
| `files`           | Frames, reference images, videos, and voice clips from **File: Add**, each under its input name. |
| `model`           | The model ID, such as `bytedance/seedance-2-5`. The default is `wan/3-0-video`.                  |
| `duration`        | `default`, or `custom` and the length in seconds.                                                |
| `resolution`      | `default`, or `custom` and a size, such as `480P` or `720p`, as the model writes it.             |
| `aspect_ratio`    | `default`, or `custom` and a shape, such as `9:16`.                                              |
| `seed`            | `default`, or `custom` and a number.                                                             |
| `run_number`      | Change this number to send the same request again.                                               |
| `prompt`          | The text sent as the model's `prompt`. Leave it empty for a model without one.                   |
| `negative_prompt` | What to leave out, for a model that takes it. Empty sends nothing.                               |
| `arguments`       | The model's other inputs as JSON, under KIE's names, such as `{"audio": false}`.                 |

Each setting at `default` sends nothing, so the model uses its own default.
Some defaults cost more, such as 1080P on `wan/3-0-video`, so set the size you
need. Models write their sizes differently, such as `480P` or `480p`;
**Model: Info** lists the choices of a model. A list input, such as
`reference_audio_urls`, always gets a list, even with one file.

## Outputs

| Output   | What it carries                                               |
| -------- | ------------------------------------------------------------- |
| `video`  | The video the model made.                                     |
| `files`  | The link of every file the model made, for the next KIE node. |
| `result` | The whole result from KIE, as JSON.                           |

## Use

1. Type the model ID in `model`, and write the prompt.
2. Set `duration` and `resolution` to `custom`, and type the length and the
   size you need.
3. Connect frames, reference images, or voice clips through **File: Add**.
4. Connect `video` to **Save Video**, and select **Run**.

A cancel stops only the wait. KIE has no cancel, so the video keeps running,
and KIE bills it. **Task: Download** collects it later.

[KIE video models](https://kie.ai/market)
