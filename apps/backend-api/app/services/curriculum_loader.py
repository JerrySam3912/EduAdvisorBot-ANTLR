from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class CurriculumConfig:
    major: str
    cohort: str
    file_name: str


class CurriculumLoader:
    def __init__(self, data_dir: str | None = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).resolve().parents[1] / "data"
        self.index_path = self.data_dir / "curriculum_index.json"

    @lru_cache(maxsize=1)
    def _load_index(self) -> dict:
        with self.index_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def resolve_file_name(self, major: str, cohort: str) -> str:
        index = self._load_index()
        key = f"{major.lower()}:{cohort.lower()}"
        file_name = index.get("curricula", {}).get(key)
        if file_name:
            return file_name

        default_major = index.get("default_major_by_cohort", {}).get(cohort.lower())
        if default_major:
            fallback_key = f"{default_major}:{cohort.lower()}"
            file_name = index.get("curricula", {}).get(fallback_key)
            if file_name:
                return file_name

        # New cohort/major fallback rules: K22 reuses K21, and DS/IT-CE can reuse K21 when needed.
        if cohort.lower() == "k22":
            fallback_key = f"{major.lower()}:k21"
            file_name = index.get("curricula", {}).get(fallback_key)
            if file_name:
                return file_name

        raise FileNotFoundError(f"No curriculum file configured for major={major}, cohort={cohort}")

    def load_curriculum(self, major: str, cohort: str) -> dict:
        file_name = self.resolve_file_name(major, cohort)
        path = self.data_dir / file_name
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
