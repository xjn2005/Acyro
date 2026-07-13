from pathlib import Path

import pytest

from acyro import TaskStatus, clear_registry, run, task


def test_run_executes_registry_in_dependency_order(tmp_path: Path) -> None:
    clear_registry()
    calls: list[str] = []

    @task
    def first() -> None:
        calls.append("first")

    @task(depends=[first])
    def second() -> None:
        calls.append("second")

    run(cache_dir=tmp_path / "cache")

    assert calls == ["first", "second"]
    assert first.status is TaskStatus.SUCCESS
    assert second.status is TaskStatus.SUCCESS


def test_run_stops_after_failure_and_preserves_original_error(tmp_path: Path) -> None:
    clear_registry()
    calls: list[str] = []

    @task
    def failing() -> None:
        calls.append("failing")
        raise ValueError("broken")

    @task(depends=[failing])
    def blocked() -> None:
        calls.append("blocked")

    with pytest.raises(ValueError, match="broken"):
        run(cache_dir=tmp_path / "cache")

    assert calls == ["failing"]
    assert failing.status is TaskStatus.FAILED
    assert blocked.status is TaskStatus.PENDING


def test_run_uses_default_cache_and_skips_unchanged_tasks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    clear_registry()
    calls: list[str] = []

    @task
    def build() -> None:
        calls.append("build")

    run()
    run()

    assert calls == ["build"]
    assert build.status is TaskStatus.SKIPPED
    assert list((tmp_path / ".acyro" / "cache").glob("*.json"))


def test_dependency_change_invalidates_downstream_task(tmp_path: Path) -> None:
    clear_registry()
    calls: list[str] = []
    cache_dir = tmp_path / "cache"

    @task
    def dependency() -> None:
        calls.append("dependency-v1")

    @task(depends=[dependency])
    def downstream() -> None:
        calls.append("downstream")

    run(cache_dir=cache_dir)

    def changed_dependency() -> None:
        calls.append("dependency-v2")

    dependency.func = changed_dependency
    run(cache_dir=cache_dir)

    assert calls == ["dependency-v1", "downstream", "dependency-v2", "downstream"]
    assert dependency.status is TaskStatus.SUCCESS
    assert downstream.status is TaskStatus.SUCCESS


def test_failed_execution_preserves_previous_cache_record(tmp_path: Path) -> None:
    clear_registry()
    cache_dir = tmp_path / "cache"

    @task
    def build() -> None:
        pass

    run(cache_dir=cache_dir)
    record_path = next(cache_dir.glob("*.json"))
    successful_record = record_path.read_bytes()

    def failing_build() -> None:
        raise RuntimeError("broken")

    build.func = failing_build
    with pytest.raises(RuntimeError, match="broken"):
        run(cache_dir=cache_dir)

    assert build.status is TaskStatus.FAILED
    assert record_path.read_bytes() == successful_record
