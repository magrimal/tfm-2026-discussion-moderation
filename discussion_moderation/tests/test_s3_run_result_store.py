"""Tests for S3RunResultStore backend."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from discussion_moderation.evals.models import (
    MANIFEST_FILENAME,
    EvalRunManifest,
    EvalRunSummary,
)
from discussion_moderation.evals.s3_store import S3RunResultStore


@pytest.fixture
def store() -> S3RunResultStore:
    """Return an S3RunResultStore configured for tests."""
    return S3RunResultStore(
        bucket="test-bucket",
        prefix="runs",
        env_name="test",
    )


@pytest.fixture
def minimal_manifest() -> EvalRunManifest:
    """Return a minimal valid EvalRunManifest."""
    return EvalRunManifest(
        run_id="2026-01-01T10-00-test-run",
        run_name="test-run",
        timestamp="2026-01-01T10:00:00+00:00",
        run_kind="evaluation",
        status="completed",
        model_count=0,
        thread_count=0,
        total_runs=0,
        completed_runs=0,
        error_count=0,
        avg_duration_ms=0,
        models={},
    )


def test_save_run_puts_manifest(store, minimal_manifest):
    """save_run() writes the manifest JSON to the expected S3 key."""
    with patch("discussion_moderation.evals.s3_store.boto3") as mock_boto3:
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3

        store.save_run(minimal_manifest)

        mock_s3.put_object.assert_called_once_with(
            Bucket="test-bucket",
            Key=("runs/test/2026-01-01T10-00-test-run/" + MANIFEST_FILENAME),
            Body=minimal_manifest.model_dump_json(indent=2).encode("utf-8"),
            ContentType="application/json",
        )


def test_save_run_puts_summary_when_provided(store, minimal_manifest):
    """save_run() writes summary.md to S3 when summary_markdown is given."""
    with patch("discussion_moderation.evals.s3_store.boto3") as mock_boto3:
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3

        store.save_run(minimal_manifest, summary_markdown="## Summary")

        assert mock_s3.put_object.call_count == 2
        summary_call = mock_s3.put_object.call_args_list[1]
        assert summary_call.kwargs["Key"].endswith("/summary.md")
        assert summary_call.kwargs["Body"] == b"## Summary"


def test_save_run_skips_summary_when_none(store, minimal_manifest):
    """save_run() does not write summary.md when summary_markdown is None."""
    with patch("discussion_moderation.evals.s3_store.boto3") as mock_boto3:
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3

        store.save_run(minimal_manifest, summary_markdown=None)

        assert mock_s3.put_object.call_count == 1


def test_list_runs_returns_summaries(store, minimal_manifest):
    """list_runs() parses manifests from S3 listing and returns summaries."""
    manifest_key = "runs/test/2026-01-01T10-00-test-run/" + MANIFEST_FILENAME
    with patch("discussion_moderation.evals.s3_store.boto3") as mock_boto3:
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        mock_s3.list_objects_v2.return_value = {
            "Contents": [{"Key": manifest_key}]
        }
        mock_s3.get_object.return_value = {
            "Body": MagicMock(
                read=lambda: minimal_manifest.model_dump_json(indent=2).encode(
                    "utf-8"
                )
            )
        }

        result = store.list_runs()

        assert len(result) == 1
        assert isinstance(result[0], EvalRunSummary)
        assert result[0].run_id == "2026-01-01T10-00-test-run"


def test_list_runs_returns_empty_when_no_contents(store):
    """list_runs() returns an empty list when the prefix has no objects."""
    with patch("discussion_moderation.evals.s3_store.boto3") as mock_boto3:
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        mock_s3.list_objects_v2.return_value = {}

        result = store.list_runs()

        assert result == []


def test_get_run_returns_detail(store, minimal_manifest):
    """get_run() fetches and returns an EvalRunDetail for a known run_id."""
    with patch("discussion_moderation.evals.s3_store.boto3") as mock_boto3:
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        mock_s3.get_object.return_value = {
            "Body": MagicMock(
                read=lambda: minimal_manifest.model_dump_json(indent=2).encode(
                    "utf-8"
                )
            )
        }

        from discussion_moderation.evals.models import EvalRunDetail

        result = store.get_run("2026-01-01T10-00-test-run")

        assert isinstance(result, EvalRunDetail)
        assert result.run_id == "2026-01-01T10-00-test-run"


def test_get_run_returns_none_on_missing_key(store):
    """get_run() returns None when the manifest key does not exist in S3."""
    from botocore.exceptions import ClientError

    with patch("discussion_moderation.evals.s3_store.boto3") as mock_boto3:
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        mock_s3.get_object.side_effect = ClientError(
            {"Error": {"Code": "NoSuchKey", "Message": "Not found"}},
            "GetObject",
        )

        result = store.get_run("nonexistent-run")

        assert result is None
