"""Check that the shipped browser bundle equals a fresh build of web/scripts."""

import sys
import asyncio

from scripts.paths import REPO_ROOT, WEB_FOLDER, FRONTEND_CHECK_FOLDER

# The files esbuild writes: the bundle, and the stylesheet its imports pull in.
BUILT_FILES = ('extension.js', 'extension.css')


async def _build_bundle() -> bool:
    """Run the build script of package.json with its output in the scratch folder, and return whether it passed.

    Returns:
        Whether the build exited without an error.

    """
    FRONTEND_CHECK_FOLDER.mkdir(parents=True, exist_ok=True)
    process = await asyncio.create_subprocess_exec(
        'bun', 'run', '--no-install', 'build', f'--outfile={FRONTEND_CHECK_FOLDER / BUILT_FILES[0]}', cwd=REPO_ROOT
    )
    return await process.wait() == 0


def main() -> int:
    """Build the bundle into the scratch folder, and report each shipped file that differs.

    Returns:
        The exit code, which is zero only when the build passed and every shipped file matches it.

    """
    if not asyncio.run(_build_bundle()):
        problems = ['esbuild failed.']
    else:
        problems = [
            f'Rebuild web/{name} with bun run build.'
            for name in BUILT_FILES
            if not (shipped := WEB_FOLDER / name).is_file()
            or shipped.read_bytes() != (FRONTEND_CHECK_FOLDER / name).read_bytes()
        ]
    for problem in problems:
        sys.stderr.write(problem + '\n')
    return int(bool(problems))


if __name__ == '__main__':
    raise SystemExit(main())
