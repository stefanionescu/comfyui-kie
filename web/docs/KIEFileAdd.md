# File: Add

Gives a KIE model a file: a public `https://` link, images, masks, audio, or
video from ComfyUI, or the files of another KIE node. You name the input of the
model in `field`, exactly as KIE writes it, such as `image_urls`. Chain several
of these nodes to give a model several files. It sends nothing; the KIE node
uploads local files when it runs.

## Inputs

| Input   | What it takes                                                                              |
| ------- | ------------------------------------------------------------------------------------------ |
| `files` | Files from another **File: Add**. The new files go after them.                             |
| `field` | The input of the model, such as `image_urls` or `reference_audio_urls`.                    |
| `file`  | A public `https://` link typed here, or a connected image, mask, audio, video, or `files`. |

## Outputs

| Output  | What it carries                                 |
| ------- | ----------------------------------------------- |
| `files` | The earlier files, then the new ones, in order. |

## Use

1. Type the input of the model into `field`. **Model: Info** lists them.
2. Connect what you want to add to `file`, or type a link into it.
3. Connect `files` to the `files` input of a KIE node, or to another
   **File: Add** to add more.

A list input takes the files in order; other inputs take exactly one file.
Some models read a list by position, such as "Image1" in the prompt. KIE
deletes uploaded files after 24 hours.

[KIE file uploads](https://docs.kie.ai/file-upload-api/quickstart)
