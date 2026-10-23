# Audio: Generate

Runs any KIE model that makes audio: speech, music, and sound effects. It
outputs every audio file and the link of every file the model made.

## Inputs

| Input        | What it takes                                                                                        |
| ------------ | ---------------------------------------------------------------------------------------------------- |
| `files`      | Audio or other files from **File: Add**, each under its input name.                                  |
| `model`      | The model ID, such as `ai-music-api/generate`. The default is `elevenlabs/text-to-speech-turbo-2-5`. |
| `run_number` | Change it to send the same request again.                                                            |
| `voice`      | The voice ID, for a voice model. The default is James, on ElevenLabs. Empty sends nothing.           |
| `prompt`     | What to make, for a music or sound model. Sent as the input named `prompt`.                          |
| `text`       | The words to speak, for a voice model. Sent as the input named `text`.                               |
| `arguments`  | Other inputs of the model as JSON, such as `{"speed": 1.1}`.                                         |

Each text input goes under its own name, and only a model with an input of
that name takes it. Clear `voice` for a model without one. **Model: Info** lists
the inputs of a model, and the voices a voice model takes.

## Outputs

| Output   | What it carries                                               |
| -------- | ------------------------------------------------------------- |
| `audio`  | Every audio file the model made, such as two songs.           |
| `files`  | The link of every file the model made, for the next KIE node. |
| `result` | The whole result from KIE, as JSON.                           |

## Use

1. Type the model ID in `model`.
2. For speech, write the words in `text`, and choose a voice in `voice`. For
   music or a sound, write `prompt`, and set the rest in `arguments`.
3. Connect `audio` to **Save Audio**, and select **Run**.

[KIE audio models](https://kie.ai/market)
