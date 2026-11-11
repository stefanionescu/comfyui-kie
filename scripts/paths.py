"""The repository folders and files the build scripts read and write."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_FOLDER = REPO_ROOT / 'web'
HELP_FOLDER = WEB_FOLDER / 'docs'
EXAMPLES_FOLDER = REPO_ROOT / 'example_workflows'
# ComfyUI lists each file here as a subgraph blueprint in its node library, named after the file.
SUBGRAPHS_FOLDER = REPO_ROOT / 'subgraphs'
README_PATH = REPO_ROOT / 'README.md'
# The script the checks run in ComfyUI's interpreter: it loads ComfyUI on the CPU, then runs the schema export.
EXPORT_SCRIPT_PATH = REPO_ROOT / 'scripts' / 'nodes' / 'export.py'
# The scratch folder of the bundle check, which esbuild writes a fresh build into.
FRONTEND_CHECK_FOLDER = REPO_ROOT / '.artifacts' / 'frontend'

__all__ = [
    'EXAMPLES_FOLDER',
    'EXPORT_SCRIPT_PATH',
    'FRONTEND_CHECK_FOLDER',
    'HELP_FOLDER',
    'README_PATH',
    'REPO_ROOT',
    'SUBGRAPHS_FOLDER',
    'WEB_FOLDER',
]
