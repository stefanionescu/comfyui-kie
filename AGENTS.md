<!-- >>> gspot managed >>> -->

# Rules

Read `.gspot/rules/WORKING.md` and `.gspot/rules/WRITING.md` first.
Read a rule below when its sentence fits your task.
A more specific rule wins over a general one.

- `.gspot/rules/BASH.md`: when you write or change a shell script.
- `.gspot/rules/CLI.md`: when you change a command-line program that the project ships.
- `.gspot/rules/COMMENTS.md`: when you write or change a comment.
- `.gspot/rules/CSS.md`: when you change a stylesheet or the style block of a component.
- `.gspot/rules/DEPENDENCIES.md`: before you add, upgrade, or remove a dependency.
- `.gspot/rules/DOCS.md`: when you write or change documentation.
- `.gspot/rules/ERRORS.md`: when you write code that raises, catches, or reports an error.
- `.gspot/rules/GENERATED.md`: when you change a generated file, or the code that writes one.
- `.gspot/rules/GIT.md`: before you commit, push, tag, or open a pull request.
- `.gspot/rules/HTTP.md`: when you change an HTTP service.
- `.gspot/rules/JAVASCRIPT.md`: when you change JavaScript or TypeScript code.
- `.gspot/rules/NAMING.md`: when you name a file, folder, type, function, or variable.
- `.gspot/rules/OPERATIONS.md`: when you write a deployment, publishing, or remote shell script.
- `.gspot/rules/PLANNING.md`: before you write a plan.
- `.gspot/rules/PYTHON.md`: when you change Python code.
- `.gspot/rules/SAFETY.md`: when a shell script deletes files, downloads, uses `sudo`, starts background jobs, or parses JSON or YAML.
- `.gspot/rules/SECRETS.md`: when code reads, stores, or logs a secret.
- `.gspot/rules/SECURITY.md`: when code takes input from outside the program, or handles authentication, redirects, or downloads.
- `.gspot/rules/SETTINGS.md`: when you change how a program reads its settings or environment.
- `.gspot/rules/SUPPRESSIONS.md`: before you add a suppression comment or run `gspot ignore`.
- `.gspot/rules/TASKS.md`: when you change `mise` tasks, `package.json` scripts, a `Makefile`, or another task runner.
- `.gspot/rules/TESTING.md`: when you write or change a test.
- `.gspot/rules/TYPESCRIPT.md`: when you change TypeScript code.
- `.gspot/rules/TYPING.md`: when you write Python type annotations.

## Commands

The rules write `gspot` for `mise exec -- gspot`.

Before you finish a change, stage it and run `gspot check --staged --only commit`. When you commit, fix what the hook reports.

Change a setting with `gspot set`, `unset`, or `unignore`. Write the other `[[...]]` records by hand, after the user agrees, then run `gspot install`.
When `gspot check` names a new configuration, ask the user, then run the `gspot add` line it prints and `gspot install`.
Run `gspot ignore` or `gspot remove` only after the user agrees, with a reason.
After you edit a package manifest or a tsconfig, run `gspot install`.

Do not edit the files that gspot writes. `gspot/generated-files` reports an edit. Change `gspot.toml`, then run `gspot install`.

<!-- <<< gspot managed <<< -->

## This project

This repository is a ComfyUI extension that runs KIE models. Its Python code in `src/` runs inside ComfyUI, and its
browser code in `web/scripts/` ships as the built `web/extension.js` and `web/extension.css`.

- After a change in `web/scripts/`, run `bun run build` and commit both built files.
- In every node, sockets come first, then choices, numbers and toggles, and free-text fields come last. Subgraphs
  promote their inputs in the same order.
- A registered node ID never changes. A display label can change, but it changes no saved key. The help page of a node
  is `web/docs/<node ID>.md`, named with the exact registered ID.
- The type checker reads the ComfyUI install that `.mise.local.toml` names in `COMFYUI_PATH` and `COMFYUI_PYTHON`.
  `mise run deps` puts that install on the path of the project environment.
- Example workflows are `example_workflows/<family>-<two-digit number>-<task>.json`. `mise run workflows` builds them
  and the blueprints in `subgraphs/` from `scripts/workflows/descriptions/`; never edit the JSON by hand. Each workflow
  holds its own copy of the subgraphs it uses, and the README links every workflow.
- Send no paid request to KIE without the owner's approval, and state its cost first.
