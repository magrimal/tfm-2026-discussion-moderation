"""S3-backed run result store."""

from __future__ import annotations

import json

import boto3
from botocore.exceptions import ClientError

from discussion_moderation.evals.models import (
    MANIFEST_FILENAME,
    EvalRunDetail,
    EvalRunManifest,
    EvalRunSummary,
)
from discussion_moderation.evals.store import (
    RunResultStore,
    summary_from_manifest,
)


class S3RunResultStore(RunResultStore, key="s3"):
    """S3-backed run result store.

    Objects are keyed as {prefix}/{env_name}/{run_id}/{filename}.
    Reads and writes use the boto3 default credential chain (env
    vars, IAM role, or ~/.aws/credentials).
    """

    def __init__(
        self,
        bucket: str,
        prefix: str,
        env_name: str,
    ) -> None:
        """Initialise the store for the given bucket, prefix and env."""
        self.bucket = bucket
        self.prefix = prefix
        self.env_name = env_name
        # Terminal-run summaries never change once written, so caching
        # them keeps list_runs() from issuing a GET per historical run
        # on every poll - only active runs and runs seen for the first
        # time cost a real GET. Instance-level: get_run_result_store()
        # memoizes the store instance in production so this persists
        # across polls, while tests constructing this class directly
        # each get a fresh, empty cache.
        self._summary_cache: dict[str, EvalRunSummary] = {}

    def _key(self, run_id: str, filename: str) -> str:
        """Return the S3 object key for run_id and filename."""
        return f"{self.prefix}/{self.env_name}/{run_id}/{filename}"

    def save_run(
        self,
        run: EvalRunManifest,
        *,
        summary_markdown: str | None = None,
    ) -> None:
        """Write the run manifest (and optional summary) to S3."""
        s3 = boto3.client("s3")
        s3.put_object(
            Bucket=self.bucket,
            Key=self._key(run.run_id, MANIFEST_FILENAME),
            Body=run.model_dump_json(indent=2).encode("utf-8"),
            ContentType="application/json",
        )
        if summary_markdown is not None:
            s3.put_object(
                Bucket=self.bucket,
                Key=self._key(run.run_id, "summary.md"),
                Body=summary_markdown.encode("utf-8"),
                ContentType="text/markdown",
            )

    def list_runs(self) -> list[EvalRunSummary]:
        """Return all runs in the configured prefix, sorted newest first.

        Runs already cached in a terminal status are served from the
        cache instead of costing a GET - only active runs and runs
        seen for the first time hit S3.
        """
        s3 = boto3.client("s3")
        prefix = f"{self.prefix}/{self.env_name}/"
        response = s3.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        manifests: dict[str, str] = {}
        summaries: set[str] = set()
        for obj in response.get("Contents", []):
            key: str = obj["Key"]
            relative = key[len(prefix) :]
            parts = relative.split("/", 1)
            if len(parts) != 2:
                continue
            run_id, filename = parts
            if filename == MANIFEST_FILENAME:
                manifests[run_id] = key
            elif filename == "summary.md":
                summaries.add(run_id)
        runs: list[EvalRunSummary] = []
        for run_id, key in manifests.items():
            cached = self._summary_cache.get(run_id)
            if cached is not None and cached.status not in (
                "running",
                "cancelling",
            ):
                runs.append(cached)
                continue

            resp = s3.get_object(Bucket=self.bucket, Key=key)
            data = json.loads(resp["Body"].read())
            manifest = EvalRunManifest.model_validate(data)
            summary = summary_from_manifest(
                manifest,
                summary_available=run_id in summaries,
            )
            if summary.status not in ("running", "cancelling"):
                self._summary_cache[run_id] = summary
            runs.append(summary)
        return sorted(runs, key=lambda r: r.timestamp, reverse=True)

    def cancel_run(self, run_id: str) -> str | None:
        """Patch the manifest status from 'running' to 'cancelling' in S3."""
        s3 = boto3.client("s3")
        key = self._key(run_id, MANIFEST_FILENAME)
        try:
            resp = s3.get_object(Bucket=self.bucket, Key=key)
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "NoSuchKey":
                return None
            raise
        data = json.loads(resp["Body"].read())
        current = data.get("status")
        if current != "running":
            return current
        data["status"] = "cancelling"
        s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(data, indent=2).encode("utf-8"),
            ContentType="application/json",
        )
        return "cancelling"

    def get_run(self, run_id: str) -> EvalRunDetail | None:
        """Return detailed run data for run_id, or None if not found."""
        s3 = boto3.client("s3")
        key = self._key(run_id, MANIFEST_FILENAME)
        try:
            resp = s3.get_object(Bucket=self.bucket, Key=key)
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "NoSuchKey":
                return None
            raise
        data = json.loads(resp["Body"].read())
        manifest = EvalRunManifest.model_validate(data)
        summary_markdown: str | None = None
        summary_key = self._key(run_id, "summary.md")
        try:
            summary_resp = s3.get_object(Bucket=self.bucket, Key=summary_key)
            summary_markdown = summary_resp["Body"].read().decode("utf-8")
        except ClientError:
            pass
        return EvalRunDetail(
            run_id=manifest.run_id,
            run_name=manifest.run_name,
            timestamp=manifest.timestamp,
            run_type=manifest.run_type,
            run_kind=manifest.run_kind,
            status=manifest.status,
            progress_message=manifest.progress_message,
            total_runs=manifest.total_runs,
            completed_runs=manifest.completed_runs,
            error_count=manifest.error_count,
            models=manifest.models,
            summary_markdown=summary_markdown,
        )
