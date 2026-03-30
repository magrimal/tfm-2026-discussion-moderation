"""Tests for ThreadHistoryStore — ADR 0007."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from discussion_moderation.common.constants import FacilitationRole
from discussion_moderation.tools.history import (
    InMemoryThreadStore,
    InterventionRecord,
    SQLiteThreadStore,
    ThreadHistoryStore,
)


# --- Fixtures ---


def make_record(
    thread_id: str = "thread-1",
    role: FacilitationRole = FacilitationRole.SOCIAL,
    technique: str = "encourage_participation",
) -> InterventionRecord:
    return InterventionRecord(
        thread_id=thread_id,
        timestamp=datetime(2026, 3, 30, 12, 0, 0, tzinfo=UTC),
        role=role,
        technique=technique,
        reasoning="Thread stalled; social facilitation selected.",
        response_text="What do you all think about this?",
    )


# --- InterventionRecord ---


class TestInterventionRecord:
    def test_fields_are_accessible(self):
        """InterventionRecord exposes all ADR 0007 fields.

        Expected result: all six fields are readable with correct types.
        """
        record = make_record()

        assert record.thread_id == "thread-1"
        assert isinstance(record.timestamp, datetime)
        assert record.role == FacilitationRole.SOCIAL
        assert record.technique == "encourage_participation"
        assert isinstance(record.reasoning, str)
        assert isinstance(record.response_text, str)


# --- ThreadHistoryStore protocol ---


class TestThreadHistoryStoreProtocol:
    def test_in_memory_store_satisfies_protocol(self):
        """InMemoryThreadStore is a valid ThreadHistoryStore.

        Expected result: isinstance check against the Protocol passes.
        """
        store = InMemoryThreadStore()

        assert isinstance(store, ThreadHistoryStore)

    def test_sqlite_store_satisfies_protocol(self, tmp_path: Path):
        """SQLiteThreadStore is a valid ThreadHistoryStore.

        Expected result: isinstance check against the Protocol passes.
        """
        store = SQLiteThreadStore(db_path=tmp_path / "history.db")

        assert isinstance(store, ThreadHistoryStore)


# --- InMemoryThreadStore ---


class TestInMemoryThreadStore:
    def test_get_history_returns_empty_for_unknown_thread(self):
        """get_history returns [] for a thread with no interventions.

        Expected result: empty list, no error.
        """
        store = InMemoryThreadStore()

        result = store.get_history("unknown-thread")

        assert result == []

    def test_record_and_retrieve_single_intervention(self):
        """record_intervention stores a record retrievable by thread_id.

        Expected result: get_history returns the stored record.
        """
        store = InMemoryThreadStore()
        record = make_record(thread_id="thread-1")

        store.record_intervention("thread-1", record)
        result = store.get_history("thread-1")

        assert len(result) == 1
        assert result[0].technique == "encourage_participation"
        assert result[0].role == FacilitationRole.SOCIAL

    def test_multiple_interventions_on_same_thread_are_appended(self):
        """Multiple interventions on the same thread accumulate in order.

        Expected result: get_history returns all records in insertion order.
        """
        store = InMemoryThreadStore()
        first = make_record(technique="encourage_participation")
        second = make_record(technique="redistribute_attention")

        store.record_intervention("thread-1", first)
        store.record_intervention("thread-1", second)
        result = store.get_history("thread-1")

        assert len(result) == 2
        assert result[0].technique == "encourage_participation"
        assert result[1].technique == "redistribute_attention"

    def test_interventions_are_isolated_by_thread_id(self):
        """Records for different threads do not bleed into each other.

        Expected result: each thread has only its own records.
        """
        store = InMemoryThreadStore()
        store.record_intervention("thread-A", make_record(thread_id="thread-A"))
        store.record_intervention("thread-B", make_record(thread_id="thread-B"))

        assert len(store.get_history("thread-A")) == 1
        assert len(store.get_history("thread-B")) == 1
        assert store.get_history("thread-A")[0].thread_id == "thread-A"

    def test_separate_store_instances_do_not_share_state(self):
        """Two InMemoryThreadStore instances are fully independent.

        Expected result: recording in one does not affect the other.
        """
        store_a = InMemoryThreadStore()
        store_b = InMemoryThreadStore()
        store_a.record_intervention("thread-1", make_record())

        assert store_b.get_history("thread-1") == []


# --- SQLiteThreadStore ---


class TestSQLiteThreadStore:
    def test_get_history_returns_empty_for_unknown_thread(self, tmp_path: Path):
        """get_history returns [] for a thread with no interventions.

        Expected result: empty list, no error.
        """
        store = SQLiteThreadStore(db_path=tmp_path / "history.db")

        result = store.get_history("unknown-thread")

        assert result == []

    def test_record_and_retrieve_single_intervention(self, tmp_path: Path):
        """record_intervention stores a record retrievable by thread_id.

        Expected result: get_history returns the stored record.
        """
        store = SQLiteThreadStore(db_path=tmp_path / "history.db")
        record = make_record(thread_id="thread-1")

        store.record_intervention("thread-1", record)
        result = store.get_history("thread-1")

        assert len(result) == 1
        assert result[0].technique == "encourage_participation"
        assert result[0].role == FacilitationRole.SOCIAL

    def test_multiple_interventions_are_appended(self, tmp_path: Path):
        """Multiple interventions accumulate in insertion order.

        Expected result: get_history returns all records in order.
        """
        store = SQLiteThreadStore(db_path=tmp_path / "history.db")
        store.record_intervention("t1", make_record(technique="encourage_participation"))
        store.record_intervention("t1", make_record(technique="redistribute_attention"))

        result = store.get_history("t1")

        assert len(result) == 2
        assert result[0].technique == "encourage_participation"
        assert result[1].technique == "redistribute_attention"

    def test_interventions_are_isolated_by_thread_id(self, tmp_path: Path):
        """Records for different threads do not bleed into each other.

        Expected result: each thread has only its own records.
        """
        store = SQLiteThreadStore(db_path=tmp_path / "history.db")
        store.record_intervention("thread-A", make_record(thread_id="thread-A"))
        store.record_intervention("thread-B", make_record(thread_id="thread-B"))

        assert len(store.get_history("thread-A")) == 1
        assert len(store.get_history("thread-B")) == 1

    def test_persists_across_store_instances(self, tmp_path: Path):
        """Records survive creating a new store pointed at the same file.

        Expected result: a second SQLiteThreadStore on the same db file
        returns records written by the first.
        """
        db_path = tmp_path / "history.db"
        store_a = SQLiteThreadStore(db_path=db_path)
        store_a.record_intervention("thread-1", make_record())

        store_b = SQLiteThreadStore(db_path=db_path)
        result = store_b.get_history("thread-1")

        assert len(result) == 1
        assert result[0].technique == "encourage_participation"


# --- PipelineDeps integration ---


class TestPipelineDepsAcceptsHistoryStore:
    def test_pipeline_deps_accepts_history_store(self):
        """PipelineDeps can be constructed with a ThreadHistoryStore.

        Expected result: no error; history_store field is accessible.
        """
        from discussion_moderation.common.models import PipelineDeps
        from discussion_moderation.settings.config import Settings

        store = InMemoryThreadStore()
        deps = PipelineDeps(settings=Settings(), history_store=store)

        assert deps.history_store is store
