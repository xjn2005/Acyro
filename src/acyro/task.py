"""Task registration and metadata."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, overload

TaskFunc = Callable[..., Any]


class TaskStatus(StrEnum):
    """Lifecycle state for a task."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass(slots=True)
class Task:
    """A Python function plus Acyro task metadata."""

    name: str
    func: TaskFunc
    depends: tuple["Task", ...] = ()
    status: TaskStatus = TaskStatus.PENDING
    metadata: dict[str, str] = field(default_factory=dict)


_registry: dict[str, Task] = {}


def clear_registry() -> None:
    """Remove all registered tasks."""

    _registry.clear()


def get_tasks() -> dict[str, Task]:
    """Return registered tasks by name."""

    return dict(_registry)


@overload
def task(func: TaskFunc, /) -> Task: ...


@overload
def task(
    *,
    depends: Iterable[Task] | None = None,
    name: str | None = None,
) -> Callable[[TaskFunc], Task]: ...


def task(
    func: TaskFunc | None = None,
    /,
    *,
    depends: Iterable[Task] | None = None,
    name: str | None = None,
) -> Task | Callable[[TaskFunc], Task]:
    """Register a function as an Acyro task."""

    def decorate(inner: TaskFunc) -> Task:
        task_name = name or inner.__name__
        if task_name in _registry:
            raise ValueError(f"Task {task_name!r} is already registered")
        registered = Task(
            name=task_name,
            func=inner,
            depends=tuple(depends or ()),
            metadata={
                "module": inner.__module__,
                "qualname": inner.__qualname__,
            },
        )
        _registry[registered.name] = registered
        return registered

    if func is not None:
        return decorate(func)
    return decorate
