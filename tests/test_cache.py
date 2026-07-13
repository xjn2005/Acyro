import json
from datetime import datetime

from acyro.cache import Cache
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
