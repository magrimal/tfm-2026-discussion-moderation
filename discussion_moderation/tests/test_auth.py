"""Tests for HTTP Basic Auth dependency."""

from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from discussion_moderation.config import get_settings
from discussion_moderation.rest_api.auth import require_auth


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Clear the settings cache before and after each test."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _make_app() -> FastAPI:
    """Return a minimal FastAPI app with one protected endpoint."""
    app = FastAPI()

    @app.get("/protected")
    def protected(_: None = Depends(require_auth)):
        """Return ok when auth passes."""
        return {"ok": True}

    return app


def test_auth_disabled_when_password_empty(monkeypatch):
    """All requests pass when no password is configured."""
    monkeypatch.setenv("FACILITATION_ADMIN_PASSWORD", "")
    client = TestClient(_make_app())

    response = client.get("/protected")

    assert response.status_code == 200


def test_auth_rejects_request_without_credentials(monkeypatch):
    """Requests with no credentials receive 401 with WWW-Authenticate header."""
    monkeypatch.setenv("FACILITATION_ADMIN_PASSWORD", "secret")
    client = TestClient(_make_app())

    response = client.get("/protected")

    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers


def test_auth_rejects_wrong_password(monkeypatch):
    """Requests with a wrong password receive 401."""
    monkeypatch.setenv("FACILITATION_ADMIN_PASSWORD", "secret")
    client = TestClient(_make_app())

    response = client.get("/protected", auth=("admin", "wrong"))

    assert response.status_code == 401


def test_auth_accepts_correct_credentials(monkeypatch):
    """Requests with correct credentials receive 200."""
    monkeypatch.setenv("FACILITATION_ADMIN_PASSWORD", "secret")
    client = TestClient(_make_app())

    response = client.get("/protected", auth=("admin", "secret"))

    assert response.status_code == 200


def test_auth_accepts_custom_username(monkeypatch):
    """Custom username from env is accepted alongside the correct password."""
    monkeypatch.setenv("FACILITATION_ADMIN_USERNAME", "maria")
    monkeypatch.setenv("FACILITATION_ADMIN_PASSWORD", "secret")
    client = TestClient(_make_app())

    response = client.get("/protected", auth=("maria", "secret"))

    assert response.status_code == 200


def test_health_accessible_without_credentials(monkeypatch):
    """Health endpoint responds without authentication even when password is set."""
    monkeypatch.setenv("FACILITATION_ADMIN_PASSWORD", "secret")
    from discussion_moderation.rest_api.main import create_app
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200


def test_protected_endpoint_requires_auth(monkeypatch, tmp_path):
    """Protected endpoints return 401 when no credentials are provided."""
    monkeypatch.setenv("FACILITATION_ADMIN_PASSWORD", "secret")
    from discussion_moderation.evals import artifacts
    monkeypatch.setattr(artifacts, "RESULTS_DIR", tmp_path)
    from discussion_moderation.rest_api.main import create_app
    client = TestClient(create_app())

    response = client.get("/api/runs")

    assert response.status_code == 401


def test_protected_endpoint_accessible_with_correct_credentials(
    monkeypatch, tmp_path
):
    """Protected endpoints return 200 when correct credentials are provided."""
    monkeypatch.setenv("FACILITATION_ADMIN_PASSWORD", "secret")
    from discussion_moderation.evals import artifacts
    monkeypatch.setattr(artifacts, "RESULTS_DIR", tmp_path)
    from discussion_moderation.rest_api.main import create_app
    client = TestClient(create_app())

    response = client.get("/api/runs", auth=("admin", "secret"))

    assert response.status_code == 200
