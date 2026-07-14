"""Tests for application settings defaults and env var loading."""

from __future__ import annotations

import pytest

from discussion_moderation.config import Settings, get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Clear the settings cache before and after each test."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_s3_bucket_default_is_empty():
    """s3_bucket defaults to an empty string."""
    settings = Settings()

    assert settings.s3_bucket == ""


def test_s3_prefix_default_is_runs():
    """s3_prefix defaults to 'runs'."""
    settings = Settings()

    assert settings.s3_prefix == "runs"


def test_env_name_default_is_local():
    """env_name defaults to 'local'."""
    settings = Settings()

    assert settings.env_name == "local"


def test_s3_bucket_loaded_from_env(monkeypatch):
    """FACILITATION_S3_BUCKET populates s3_bucket."""
    monkeypatch.setenv(
        "FACILITATION_S3_BUCKET", "tfm-2026-discussion-moderation"
    )
    settings = Settings()

    assert settings.s3_bucket == "tfm-2026-discussion-moderation"


def test_env_name_loaded_from_env(monkeypatch):
    """FACILITATION_ENV populates env_name."""
    monkeypatch.setenv("FACILITATION_ENV", "ec2")
    settings = Settings()

    assert settings.env_name == "ec2"
