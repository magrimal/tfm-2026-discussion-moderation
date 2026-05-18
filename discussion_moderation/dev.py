"""Local development bootstrap and launcher commands."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = REPO_ROOT / "dashboard"


def _npm_executable() -> str:
    return "npm.cmd" if sys.platform.startswith("win") else "npm"


def _require_executable(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise SystemExit(
            f"Required executable '{name}' was not found in PATH."
        )
    return executable


def _frontend_install_command() -> list[str]:
    npm = _require_executable(_npm_executable())
    return [npm, "install"]


def _frontend_dev_command() -> list[str]:
    npm = _require_executable(_npm_executable())
    return [npm, "run", "dev"]


def _backend_dev_command() -> list[str]:
    return [
        sys.executable,
        "-m",
        "uvicorn",
        "discussion_moderation.rest_api.main:app",
        "--reload",
    ]


def _run_checked(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def _ensure_frontend_installed() -> None:
    if (DASHBOARD_DIR / "node_modules").exists():
        return
    print("dashboard dependencies missing, running setup...", flush=True)
    setup()


def _spawn(command: list[str], cwd: Path) -> subprocess.Popen[bytes]:
    return subprocess.Popen(command, cwd=cwd)


def setup() -> None:
    if not DASHBOARD_DIR.exists():
        raise SystemExit(f"Dashboard directory not found: {DASHBOARD_DIR}")

    print("Installing dashboard dependencies...", flush=True)
    _run_checked(_frontend_install_command(), DASHBOARD_DIR)
    print("Frontend bootstrap complete.", flush=True)


def up() -> None:
    _ensure_frontend_installed()

    print("Starting backend and dashboard...", flush=True)
    backend = _spawn(_backend_dev_command(), REPO_ROOT)
    frontend = _spawn(_frontend_dev_command(), DASHBOARD_DIR)
    processes = [backend, frontend]

    try:
        while True:
            for process in processes:
                return_code = process.poll()
                if return_code is not None:
                    _stop_processes(processes)
                    raise SystemExit(return_code)
            time.sleep(0.5)
    except KeyboardInterrupt:
        _stop_processes(processes)


def _stop_processes(processes: list[subprocess.Popen[bytes]]) -> None:
    for process in processes:
        if process.poll() is None:
            process.terminate()
    for process in processes:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap and run the local development stack."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("setup", help="Install dashboard dependencies")
    subparsers.add_parser(
        "up", help="Start the backend API and dashboard together"
    )

    args = parser.parse_args(argv)

    if args.command == "setup":
        setup()
        return
    if args.command == "up":
        up()
        return

    raise SystemExit(f"Unsupported command: {args.command}")