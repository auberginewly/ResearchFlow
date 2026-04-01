from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from src.config import settings


class FileCache:
    def __init__(self, namespace: str) -> None:
        self.cache_dir = Path(settings.cache_storage_dir) / namespace
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _build_path(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.json"

    def get(self, key: str) -> Any | None:
        path = self._build_path(key)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def set(self, key: str, value: Any) -> None:
        path = self._build_path(key)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
