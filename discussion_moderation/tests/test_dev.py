from pathlib import Path

from discussion_moderation import dev


def test_dashboard_dir_points_to_repo_dashboard():
    assert dev.DASHBOARD_DIR.name == "dashboard"
    assert (dev.DASHBOARD_DIR / "package.json").exists()


def test_backend_dev_command_uses_uvicorn_module():
    command = dev._backend_dev_command()

    assert command[1:3] == ["-m", "uvicorn"]
    assert command[3] == "discussion_moderation.rest_api.main:app"
    assert command[4:] == ["--reload"]


def test_repo_root_contains_pyproject():
    assert isinstance(dev.REPO_ROOT, Path)
    assert (dev.REPO_ROOT / "pyproject.toml").exists()