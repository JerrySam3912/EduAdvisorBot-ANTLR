from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionState:
    session_id: str
    last_course_code: str | None = None
    last_course_name: str | None = None
    last_cohort: str | None = None
    last_major: str | None = None
    last_intent: str | None = None
    last_student_id: str | None = None
    last_semester_code: str | None = None
    onboarding_complete: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class SessionMemoryService:
    def __init__(self):
        self._store: dict[str, SessionState] = {}

    def get(self, session_id: str | None) -> SessionState | None:
        if not session_id:
            return None
        return self._store.get(session_id)

    def get_or_create(self, session_id: str | None) -> SessionState | None:
        if not session_id:
            return None
        if session_id not in self._store:
            self._store[session_id] = SessionState(session_id=session_id)
        return self._store[session_id]

    def update(self, session_id: str | None, **kwargs: Any) -> SessionState | None:
        state = self.get_or_create(session_id)
        if not state:
            return None
        for key, value in kwargs.items():
            if hasattr(state, key) and value is not None:
                setattr(state, key, value)
            elif value is not None:
                state.metadata[key] = value
        return state

    def clear(self, session_id: str | None) -> None:
        if session_id and session_id in self._store:
            del self._store[session_id]
