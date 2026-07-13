import json
from datetime import datetime
from pathlib import Path

import pytest

from acyro.cache import Cache
from acyro.exceptions import InputNotFoundError
from acyro.task import Task


def test_cache_writes_success_metadata_and_detects_hit(tmp_path) -> None:
    task = Task(
        name="build",
        func=lambda: None,
        metadata={"module": "workflow", "qualname": "build"},
    )
    cache = Cache(tmp_path)

    assert not cache.is_current(task)

    cache.write(task, duration_seconds=0.25)

    record = json.loads(next(tmp_path.glob("*.json")).read_text(encoding="utf-8"))
    assert record.keys() == {
        "task_name",
        "fingerprint",
        "timestamp",
        "duration_seconds",
        "status",
        "outputs",
    }
    assert record["task_name"] == "build"
    assert record["fingerprint"] == cache.fingerprint(task)
    assert datetime.fromisoformat(record["timestamp"]).tzinfo is not None
    assert record["duration_seconds"] == 0.25
    assert record["status"] == "success"
    assert cache.is_current(task)


def test_corrupted_cache_record_is_a_miss(tmp_path) -> None:
    task = Task(name="build", func=lambda: None)
    cache = Cache(tmp_path)
    cache.write(task, duration_seconds=0.0)
    next(tmp_path.glob("*.json")).write_text("not json", encoding="utf-8")

    assert not cache.is_current(task)


def test_input_content_change_invalidates_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "source.txt"
    source.write_text("first", encoding="utf-8")
    task = Task(name="build", func=lambda: None, inputs=("source.txt",))
    cache = Cache(tmp_path / "cache")

    cache.write(task, duration_seconds=0.0)
    assert cache.is_current(task)

    source.write_text("second", encoding="utf-8")

    assert not cache.is_current(task)


def test_unmatched_input_glob_raises_clear_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    task = Task(name="build", func=lambda: None, inputs=("src/**/*.py",))

    with pytest.raises(InputNotFoundError, match=r"build.*src/\*\*/\*\.py"):
        Cache(tmp_path / "cache").is_current(task)


def test_modified_or_missing_output_invalidates_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "result.txt"
    output.write_text("first", encoding="utf-8")
    task = Task(name="build", func=lambda: None, outputs=("result.txt",))
    cache = Cache(tmp_path / "cache")
    cache.write(task, duration_seconds=0.0)

    output.write_text("changed", encoding="utf-8")
    assert not cache.is_current(task)

    output.unlink()
    assert not cache.is_current(task)
