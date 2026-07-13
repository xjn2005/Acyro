"""Task execution in dependency order."""

from pathlib import Path
from time import perf_counter

from acyro.cache import Cache
from acyro.dag import build_dag
from acyro.task import Task, TaskStatus, get_tasks


def run(
    tasks: dict[str, Task] | None = None,
    *,
    cache_dir: str | Path = Path(".acyro/cache"),
) -> None:
    """Run tasks serially in dependency order."""

    selected = get_tasks() if tasks is None else tasks
    cache = Cache(Path(cache_dir))
    for task in selected.values():
        task.status = TaskStatus.PENDING

    for task in build_dag(selected).topological_sort():
        if cache.is_current(task):
            task.status = TaskStatus.SKIPPED
            continue
        task.status = TaskStatus.RUNNING
        started = perf_counter()
        try:
            task.func()
        except Exception:
            task.status = TaskStatus.FAILED
            raise
        task.status = TaskStatus.SUCCESS
        cache.write(task, perf_counter() - started)
