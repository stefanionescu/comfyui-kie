<!-- >>> gspot managed >>> -->

# Rules

Read these rules first:

- `.gspot/configurations/general/engineering/rules/WORKING.md`
- `.gspot/configurations/general/prose/rules/WRITING.md`
- `.gspot/configurations/general/engineering/rules/TALKING.md`

Read a rule below when its sentence fits your task.
A rule marked `in <folder>/` applies only to files in that folder.
A more specific rule wins over a general one.

## Languages

- `.gspot/configurations/language/bash/rules/BASH.md`: when you write or change a shell script.
- `.gspot/configurations/language/bash/rules/OPERATIONS.md`: when you write a deployment, publishing, or remote shell script.
- `.gspot/configurations/language/bash/rules/SAFETY.md`: when a shell script deletes files, downloads, uses `sudo`, starts background jobs, or parses JSON or YAML.
- `.gspot/configurations/language/javascript/rules/BUN.md`: when code runs on Bun.
- `.gspot/configurations/language/javascript/rules/JAVASCRIPT.md`: when you change JavaScript or TypeScript code.
- `.gspot/configurations/language/python/rules/PACKAGING.md`: when you change Python dependencies, lockfiles, or package layout.
- `.gspot/configurations/language/python/rules/PYTHON.md`: when you change Python code.
- `.gspot/configurations/language/python/rules/TYPING.md`: when you write Python type annotations.
- `.gspot/configurations/language/typescript/rules/TYPESCRIPT.md`: when you change TypeScript code.
- `.gspot/configurations/language/css/rules/CSS.md`: when you change a stylesheet.

## General

- `.gspot/configurations/general/commits/rules/GIT.md`: before you commit, push, tag, or open a pull request.
- `.gspot/configurations/general/data-files/rules/YAML.md`: when you change a `.yml` or `.yaml` file.
- `.gspot/configurations/general/dependencies/rules/DEPENDENCIES.md`: before you add, upgrade, or remove a dependency.
- `.gspot/configurations/general/docs/rules/DOCS.md`: when you write or change documentation.
- `.gspot/configurations/general/engineering/rules/CLI.md`: when you change a command-line program that the project ships.
- `.gspot/configurations/general/engineering/rules/COMMENTS.md`: when you write or change a comment.
- `.gspot/configurations/general/engineering/rules/ERRORS.md`: when you write code that raises, catches, or reports an error.
- `.gspot/configurations/general/engineering/rules/HTTP.md`: when you change an HTTP service.
- `.gspot/configurations/general/engineering/rules/PLANNING.md`: before you write a plan.
- `.gspot/configurations/general/engineering/rules/SETTINGS.md`: when you change how a program reads its settings or environment.
- `.gspot/configurations/general/engineering/rules/TASKS.md`: when you change `mise` tasks, `package.json` scripts, a `Makefile`, or another task runner.
- `.gspot/configurations/general/engineering/rules/TESTING.md`: when you write or change a test.
- `.gspot/configurations/general/gspot/rules/GENERATED.md`: when you change a generated file, or the code that writes one.
- `.gspot/configurations/general/gspot/rules/SUPPRESSIONS.md`: before you add a suppression comment or run `gspot ignore`.
- `.gspot/configurations/general/naming/rules/NAMING.md`: when you name a file, folder, type, function, or variable.
- `.gspot/configurations/general/secrets/rules/SECRETS.md`: when code reads, stores, or logs a secret.
- `.gspot/configurations/general/security/rules/SECURITY.md`: when code handles input, authentication, redirects, or downloads.

## Commands

The rules write `gspot` for `bun run --no-install gspot`.

Before you commit, run `bun run --no-install gspot check --staged`.

To change `gspot.toml`, run `bun run --no-install gspot set`, `unset`, `add`, `remove`, `ignore`, or `unignore`.
After you edit `gspot.toml` by hand, run `bun run --no-install gspot apply`.

## Generated files

Do not edit these files. Change `gspot.toml`, then run `bun run --no-install gspot apply`.

- every file under `.gspot/`
- `.editorconfig`
- `.github/workflows/gspot.yml`
- `.markdownlint.jsonc`
- `.prettierignore`
- `.stylelintrc.json`
- `eslint.config.mjs`
- `prettier.config.mjs`
- `pyrightconfig.json`
- `ruff.toml`

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
