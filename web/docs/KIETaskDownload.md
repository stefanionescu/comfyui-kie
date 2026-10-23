# Task: Download

Downloads what KIE made for a task after a run stopped: you cancelled it while
KIE was running it, ComfyUI restarted, or it ran longer than the request
timeout. It bills nothing.

## Inputs

| Input  | What it takes                                                                 |
| ------ | ----------------------------------------------------------------------------- |
| `task` | A task started on this server, shown as its ID, model, and start time in UTC. |

## Outputs

| Output   | What it carries                                             |
| -------- | ----------------------------------------------------------- |
| `images` | Every image the task made.                                  |
| `masks`  | The mask of every image, from its transparency.             |
| `video`  | Every video the task made.                                  |
| `audio`  | Every audio file the task made.                             |
| `files`  | The link of every file the task made, for another KIE node. |
| `result` | The whole result from KIE, as JSON.                         |

## Use

1. Choose the task in `task`. Press R to list tasks started after the page
   loaded.
2. Connect the output you need, such as `video` to **Save Video**.
3. Select **Run**.

A task leaves the list once the node downloads its files, or when it fails. KIE
keeps the files of a task for 14 days. Outputs the task did not make stop the
nodes connected to them.

[KIE task details](https://docs.kie.ai/market/common/get-task-detail)
