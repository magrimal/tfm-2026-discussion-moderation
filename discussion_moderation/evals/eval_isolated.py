"""Run eval-models in an isolated git worktree.

Creates a temporary worktree pinned to the current branch so you can
switch branches freely while the experiment runs. Results are written
directly to the main checkout's docs/experiments/results/ via a
symlink, so they are immediately available after the run.

Usage:
    uv run --env-file .env.local eval-models-isolated
    uv run --env-file .env.local eval-models-isolated 2>&1 | tee /tmp/eval.log

All arguments are forwarded to eval-models. Environment variables
(EVAL_MODELS, EVAL_THREADS, etc.) are inherited from the caller.

The worktree is removed on exit. If the run is interrupted and the
worktree is left behind, clean it up with:
    git worktree prune
"""

import atexit
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path


def main() -> None:
    """Create a worktree, run eval-models inside it, then clean up."""
    repo_root = Path(__file__).parents[2]

    branch = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=repo_root, text=True
    ).strip()
    if not branch:
        print("error: not on a named branch", file=sys.stderr)
        sys.exit(1)

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    worktree_path = Path(tempfile.gettempdir()) / f"eval-worktree-{timestamp}"

    print(f"[eval-isolated] branch: {branch}", flush=True)
    print(f"[eval-isolated] worktree: {worktree_path}", flush=True)

    subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree_path), "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )

    def _cleanup() -> None:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree_path)],
            cwd=repo_root,
            capture_output=True,
        )

    atexit.register(_cleanup)

    # Point the worktree's results dir at the main checkout so results
    # land in the right place without any post-run copy step.
    main_results = repo_root / "docs" / "experiments" / "results"
    worktree_results = worktree_path / "docs" / "experiments" / "results"
    if worktree_results.exists():
        shutil.rmtree(worktree_results)
    worktree_results.symlink_to(main_results)

    # Copy .env.local if present — it's gitignored so not in the worktree.
    env_file = repo_root / ".env.local"
    if env_file.exists():
        shutil.copy(env_file, worktree_path / ".env.local")
        env_flag = ["--env-file", ".env.local"]
    else:
        env_flag = []

    cmd = ["uv", "run", *env_flag, "eval-models", *sys.argv[1:]]
    result = subprocess.run(cmd, cwd=worktree_path)
    sys.exit(result.returncode)
