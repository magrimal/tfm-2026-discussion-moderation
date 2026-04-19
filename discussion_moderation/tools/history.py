"""Intervention history store (ADR 0007).

Provides per-thread history of facilitation interventions. Used by
the role agents for cooldown checks and EMT escalation tracking.

Two implementations ship with the PoC:
- InMemoryThreadStore: plain dict, resets on restart. For dev/tests.
- SQLiteThreadStore: local file, survives restarts. For the thesis PoC.

Both satisfy the ThreadHistoryStore Protocol, which is the only type
the pipeline uses. Swapping backends is a PipelineDeps config change.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

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


@runtime_checkable
class ThreadHistoryStore(Protocol):
    """Protocol for intervention history backends.

    Uses a Protocol (structural typing) so backends are independent
    of this definition. Same pattern as LMSBackend in tools/base.py.
    Implementations must be injectable via PipelineDeps.
    """

    def get_history(self, thread_id: str) -> list[InterventionRecord]:
        """Return all recorded interventions for a thread, oldest first.

        Args:
            thread_id: The discussion thread identifier.

        Returns:
            List of InterventionRecord in insertion order.
            Empty list if no interventions have been recorded.
        """
        ...

    def record_intervention(
        self, thread_id: str, record: InterventionRecord
    ) -> None:
        """Persist an intervention record for a thread.

        Args:
            thread_id: The discussion thread identifier.
            record: The intervention to store.
        """
        ...


class InMemoryThreadStore:
    """In-memory intervention history store.

    Plain dict backend. Resets when the process restarts.
    Appropriate for development and tests.
    """

    def __init__(self) -> None:
        self._store: dict[str, list[InterventionRecord]] = {}

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


class SQLiteThreadStore:
    """SQLite-backed intervention history store.

    Persists intervention records to a local SQLite file. Survives
    process restarts. Appropriate for the thesis PoC.

    Not suitable for high-concurrency production deployments;
    replace with a PostgreSQL or Redis backend for those cases.

    Attributes:
        db_path: Path to the SQLite database file.
    """

    def __init__(self, db_path: Path | str = "history.db") -> None:
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
