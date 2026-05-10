from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


class EdusoftNoticeService:
    def __init__(self, data_dir: str | None = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).resolve().parents[1] / "data"
        self.notices_path = self.data_dir / "edusoft_notices.json"

    @lru_cache(maxsize=1)
    def _load(self) -> dict:
        with self.notices_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def get_latest_drop_notice(self) -> dict | None:
        payload = self._load()
        notices = payload.get("notices", [])
        return notices[0] if notices else None
