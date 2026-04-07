"""Shared test fixtures and setup for unit tests."""

import os


def pytest_configure(config):
    """Set a dummy API key so agents can be instantiated without a live key.

    Module-level agent singletons (e.g. classification_agent) are
    constructed at import time. pydantic_ai raises UserError if no key is
    present, even when no actual API call is made. A placeholder is enough
    for unit tests that only test prompt assembly and model validation.
    """
    os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-unit-tests")
