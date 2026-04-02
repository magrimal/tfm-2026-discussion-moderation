"""Intervention history store — ADR 0007.

Provides per-thread history of facilitation interventions. Used by
the classifier for cooldown checks and by the intellectual role agent
for EMT escalation tracking.

Two implementations ship with the PoC:
- InMemoryThreadStore: plain dict, resets on restart. For dev/tests.
- SQLiteThreadStore: local file, survives restarts. For the thesis PoC.

Both satisfy the ThreadHistoryStore Protocol, which is the only type
the pipeline uses. Swapping backends is a PipelineDeps config change.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

from discussion_moderation.constants import FacilitationRole


@dataclass
class InterventionRecord:
    """A single facilitation intervention recorded by the pipeline.

    Attributes:
        thread_id: ID of the discussion thread.
        timestamp: When the intervention was generated.
        role: The facilitation role that produced the intervention.
        technique: The technique name from the ADR 0002 repertoire.
        reasoning: Full reasoning chain from classifier and orchestrator.
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

    Description:
        Defines the interface for storing and retrieving per-thread
        intervention history. Uses a Protocol (structural typing) so
        backends are independent of this definition — the same pattern
        as LMSBackend in tools/base.py.

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

    Description:
        Plain dict backend. Resets when the process restarts.
        Appropriate for development and tests.
    """

    def __init__(self) -> None:
        self._store: dict[str, list[InterventionRecord]] = {}

    def get_history(self, thread_id: str) -> list[InterventionRecord]:
        return list(self._store.get(thread_id, []))

    def record_intervention(
        self, thread_id: str, record: InterventionRecord
    ) -> None:
        if thread_id not in self._store:
            self._store[thread_id] = []
        self._store[thread_id].append(record)


_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS interventions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id   TEXT    NOT NULL,
    timestamp   TEXT    NOT NULL,
    role        TEXT    NOT NULL,
    technique   TEXT    NOT NULL,
    reasoning   TEXT    NOT NULL,
    response_text TEXT  NOT NULL
)
"""

_INSERT = """
INSERT INTO interventions
    (thread_id, timestamp, role, technique, reasoning, response_text)
VALUES (?, ?, ?, ?, ?, ?)
"""

_SELECT = """
SELECT thread_id, timestamp, role, technique, reasoning, response_text
FROM interventions
WHERE thread_id = ?
ORDER BY id ASC
"""


class SQLiteThreadStore:
    """SQLite-backed intervention history store.

    Description:
        Persists intervention records to a local SQLite file.
        Survives process restarts. Appropriate for the thesis PoC.

        Not suitable for high-concurrency production deployments;
        replace with a PostgreSQL or Redis backend for those cases.

    Attributes:
        db_path: Path to the SQLite database file.
    """

    def __init__(self, db_path: Path | str = "history.db") -> None:
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(_CREATE_TABLE)

    def get_history(self, thread_id: str) -> list[InterventionRecord]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(_SELECT, (thread_id,)).fetchall()
        return [
            InterventionRecord(
                thread_id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                role=FacilitationRole(row[2]),
                technique=row[3],
                reasoning=row[4],
                response_text=row[5],
            )
            for row in rows
        ]

    def record_intervention(
        self, thread_id: str, record: InterventionRecord
    ) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                _INSERT,
                (
                    thread_id,
                    record.timestamp.isoformat(),
                    record.role.value,
                    record.technique,
                    record.reasoning,
                    record.response_text,
                ),
            )
