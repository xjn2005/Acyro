"""Local file-based task cache."""

import inspect
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

from acyro.task import Task, TaskStatus


@dataclass(slots=True)
class Cache:
    """JSON cache records for successful tasks."""

    root: Path

    def fingerprint(self, task: Task) -> str:
        """Hash task metadata, source, and dependency fingerprints."""

        return self._fingerprint(task, {})

    def _fingerprint(self, task: Task, memo: dict[int, str]) -> str:
        if id(task) in memo:
            return memo[id(task)]
        try:
            source = inspect.getsource(task.func)
        except (OSError, TypeError):
            source = None
        payload = {
            "task_name": task.name,
            "metadata": task.metadata,
            "source": source,
            "dependencies": [
                {
                    "task_name": dependency.name,
                    "fingerprint": self._fingerprint(dependency, memo),
                }
                for dependency in sorted(task.depends, key=lambda item: item.name)
            ],
        }
        fingerprint = sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        memo[id(task)] = fingerprint
        return fingerprint

    def is_current(self, task: Task) -> bool:
        """Return whether a valid record matches the task fingerprint."""

        try:
            record = json.loads(self._path(task).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return False
        return (
            isinstance(record, dict)
            and record.get("task_name") == task.name
            and record.get("fingerprint") == self.fingerprint(task)
            and record.get("status") == TaskStatus.SUCCESS.value
        )

    def write(self, task: Task, duration_seconds: float) -> None:
        """Write a successful task record."""

        self.root.mkdir(parents=True, exist_ok=True)
        record = {
            "task_name": task.name,
            "fingerprint": self.fingerprint(task),
            "timestamp": datetime.now(UTC).isoformat(),
            "duration_seconds": duration_seconds,
            "status": TaskStatus.SUCCESS.value,
        }
        self._path(task).write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _path(self, task: Task) -> Path:
        name_hash = sha256(task.name.encode()).hexdigest()
        return self.root / f"{name_hash}.json"
