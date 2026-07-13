"""Local file-based task cache."""

import inspect
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from glob import has_magic
from hashlib import sha256
from pathlib import Path

from acyro.exceptions import InputNotFoundError, OutputNotFoundError
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
            "inputs": self._input_fingerprints(task),
            "outputs": self._output_fingerprints(task),
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

        fingerprint = self.fingerprint(task)
        outputs = self._output_fingerprints(task)
        try:
            record = json.loads(self._path(task).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return False
        return (
            isinstance(record, dict)
            and record.get("task_name") == task.name
            and record.get("fingerprint") == fingerprint
            and record.get("status") == TaskStatus.SUCCESS.value
            and record.get("outputs", []) == outputs
        )

    def write(self, task: Task, duration_seconds: float) -> None:
        """Write a successful task record."""

        outputs = self._output_fingerprints(task, required=True)
        self.root.mkdir(parents=True, exist_ok=True)
        record = {
            "task_name": task.name,
            "fingerprint": self.fingerprint(task),
            "timestamp": datetime.now(UTC).isoformat(),
            "duration_seconds": duration_seconds,
            "status": TaskStatus.SUCCESS.value,
            "outputs": outputs,
        }
        self._path(task).write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _path(self, task: Task) -> Path:
        name_hash = sha256(task.name.encode()).hexdigest()
        return self.root / f"{name_hash}.json"

    def _input_fingerprints(self, task: Task) -> list[dict[str, str]]:
        cwd = Path.cwd()
        files: dict[str, Path] = {}
        for declared in task.inputs:
            if has_magic(declared):
                matches = sorted(path for path in cwd.glob(declared) if path.is_file())
            else:
                path = cwd / declared
                matches = [path] if path.is_file() else []
            if not matches:
                raise InputNotFoundError(
                    f"Task {task.name!r} input {declared!r} was not found"
                )
            for path in matches:
                files[path.relative_to(cwd).as_posix()] = path
        return [
            {"path": name, "sha256": self._file_hash(path)}
            for name, path in sorted(files.items())
        ]

    def _output_fingerprints(
        self, task: Task, *, required: bool = False
    ) -> list[dict[str, str]] | None:
        cwd = Path.cwd()
        outputs: list[dict[str, str]] = []
        for declared in task.outputs:
            path = cwd / declared
            if not path.is_file():
                if required:
                    raise OutputNotFoundError(
                        f"Task {task.name!r} output {declared!r} was not created"
                    )
                return None
            outputs.append(
                {
                    "path": path.relative_to(cwd).as_posix(),
                    "sha256": self._file_hash(path),
                }
            )
        return outputs

    @staticmethod
    def _file_hash(path: Path) -> str:
        digest = sha256()
        with path.open("rb") as file:
            while chunk := file.read(1024 * 1024):
                digest.update(chunk)
        return digest.hexdigest()
