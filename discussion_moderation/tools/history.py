"""Intervention history store (ADR 0007).

Provides per-thread history of facilitation interventions. Used by
the role agents for cooldown checks and EMT escalation tracking.

Two implementations ship with the PoC:
- InMemoryThreadStore: plain dict, resets on restart. For dev/tests.
- SQLiteThreadStore: local file, survives restarts. For the thesis PoC.

Subclasses register themselves via key= and are resolved at runtime
through ThreadHistoryStore.for_key(key).
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import ClassVar

from sqlmodel import Field, Session, SQLModel, create_engine, select

from discussion_moderation.constants import FacilitationRole


@dataclass
class InterventionRecord:
    """A single facilitation intervention recorded by the pipeline.

    Attributes:
        thread_id: ID of the discussion thread.
        timestamp: When the intervention was generated.
        role: The facilitation role that produced the intervention.
        technique: The technique name from the ADR 0002 repertoire.
        reasoning: Full reasoning chain from classification and
            orchestration.
        response_text: The generated facilitation text.
    """

    thread_id: str
    timestamp: datetime
    role: FacilitationRole
    technique: str
    reasoning: str
    response_text: str


class ThreadHistoryStore:
    """Base class for intervention history backends.

    Subclasses register themselves automatically:

        class MyStore(ThreadHistoryStore, key="mybackend"):
            def get_history(self, thread_id: str): ...
            def record_intervention(self, thread_id, record): ...

    Use ThreadHistoryStore.for_key(key) to resolve and instantiate
    the right backend at runtime. Returns None for unregistered keys.
    """

    _registry: ClassVar[dict[str, type["ThreadHistoryStore"]]] = {}

    def __init_subclass__(cls, key: str = "", **kwargs: object) -> None:
        """Register the subclass under key."""
        super().__init_subclass__(**kwargs)
        if key:
            ThreadHistoryStore._registry[key] = cls

    @classmethod
    def for_key(cls, key: str) -> "ThreadHistoryStore | None":
        """Return an instance of the store registered under key, or None.

        Args:
            key: Backend identifier, e.g. "memory" or "sqlite".

        Returns:
            A new store instance, or None if the key is not registered.
        """
        store_cls = cls._registry.get(key)
        if store_cls is None:
            return None
        return store_cls()

    def get_history(self, thread_id: str) -> list[InterventionRecord]:
        """Return all recorded interventions for a thread, oldest first.

        Args:
            thread_id: The discussion thread identifier.

        Returns:
            List of InterventionRecord in insertion order.
        """
        raise NotImplementedError

    def record_intervention(
        self, thread_id: str, record: InterventionRecord
    ) -> None:
        """Persist an intervention record for a thread.

        Args:
            thread_id: The discussion thread identifier.
            record: The intervention to store.
        """
        raise NotImplementedError


_MEMORY_STORE_INSTANCE: "InMemoryThreadStore | None" = None


class InMemoryThreadStore(ThreadHistoryStore, key="memory"):
    """In-memory intervention history store.

    Plain dict backend. Resets when the process restarts.
    Appropriate for development and tests.

    A single instance is shared across all callers within a process so
    that interventions recorded during a pipeline run are visible to the
    history endpoint in the same server process.
    """

    def __new__(cls) -> "InMemoryThreadStore":
        """Return the shared singleton instance."""
        global _MEMORY_STORE_INSTANCE
        if _MEMORY_STORE_INSTANCE is None:
            instance = super().__new__(cls)
            instance._store = {}
            _MEMORY_STORE_INSTANCE = instance
        return _MEMORY_STORE_INSTANCE

    def __init__(self) -> None:
        """No-op: state is initialised in __new__."""

    def get_history(self, thread_id: str) -> list[InterventionRecord]:
        """Return recorded interventions for a thread.

        Args:
            thread_id: The discussion thread identifier.

        Returns:
            Copy of stored records, oldest first.
        """
        return list(self._store.get(thread_id, []))

    def record_intervention(
        self, thread_id: str, record: InterventionRecord
    ) -> None:
        """Store an intervention record.

        Args:
            thread_id: The discussion thread identifier.
            record: The intervention to store.
        """
        if thread_id not in self._store:
            self._store[thread_id] = []
        self._store[thread_id].append(record)


class InterventionRow(SQLModel, table=True):
    """SQLModel table row for persisted interventions.

    Maps directly to the interventions table. Kept separate from
    InterventionRecord (the domain type) so ORM concerns stay
    isolated to this module.
    """

    id: int | None = Field(default=None, primary_key=True)
    thread_id: str = Field(index=True)
    timestamp: str
    role: str
    technique: str
    reasoning: str
    response_text: str


class SQLiteThreadStore(ThreadHistoryStore, key="sqlite"):
    """SQLite-backed intervention history store.

    Persists intervention records to a local SQLite file. Survives
    process restarts. Appropriate for the thesis PoC.

    Not suitable for high-concurrency production deployments;
    replace with a PostgreSQL or Redis backend for those cases.

    Attributes:
        db_path: Path to the SQLite database file.
    """

    def __init__(self, db_path: Path | str = "history.db") -> None:
        """Initialize and create the database schema if needed.

        Args:
            db_path: Path to the SQLite file. Defaults to "history.db"
                in the current working directory.
        """
        self.db_path = Path(db_path)
        url = f"sqlite:///{self.db_path}"
        self._engine = create_engine(url)
        SQLModel.metadata.create_all(self._engine)

    def get_history(self, thread_id: str) -> list[InterventionRecord]:
        """Return all recorded interventions for a thread, oldest first.

        Args:
            thread_id: The discussion thread identifier.

        Returns:
            List of InterventionRecord in insertion order.
        """
        with Session(self._engine) as session:
            rows = session.exec(
                select(InterventionRow)
                .where(InterventionRow.thread_id == thread_id)
                .order_by(InterventionRow.id)
            ).all()
        return [
            InterventionRecord(
                thread_id=row.thread_id,
                timestamp=datetime.fromisoformat(row.timestamp),
                role=FacilitationRole(row.role),
                technique=row.technique,
                reasoning=row.reasoning,
                response_text=row.response_text,
            )
            for row in rows
        ]

    def record_intervention(
        self, thread_id: str, record: InterventionRecord
    ) -> None:
        """Persist an intervention record.

        Args:
            thread_id: The discussion thread identifier.
            record: The intervention to store.
        """
        row = InterventionRow(
            thread_id=thread_id,
            timestamp=record.timestamp.isoformat(),
            role=record.role.value,
            technique=record.technique,
            reasoning=record.reasoning,
            response_text=record.response_text,
        )
        with Session(self._engine) as session:
            session.add(row)
            session.commit()
