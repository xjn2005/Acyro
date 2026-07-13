"""DAG representation and topological sorting."""

from collections import deque
from dataclasses import dataclass, field

from acyro.exceptions import CycleError, UnknownDependencyError
from acyro.task import Task


@dataclass(slots=True)
class DAG:
    """A directed acyclic graph of named tasks."""

    _nodes: dict[str, Task] = field(default_factory=dict)
    _dependencies: dict[str, dict[str, None]] = field(default_factory=dict)

    @property
    def nodes(self) -> tuple[Task, ...]:
        """Return nodes in insertion order."""

        return tuple(self._nodes.values())

    def add_node(self, task: Task) -> None:
        """Add a task node."""

        self._nodes[task.name] = task
        self._dependencies.setdefault(task.name, {})

    def add_edge(self, dependency: str, task: str) -> None:
        """Record that task depends on dependency."""

        if dependency not in self._nodes:
            raise KeyError(f"Unknown node: {dependency}")
        if task not in self._nodes:
            raise KeyError(f"Unknown node: {task}")
        self._dependencies[task][dependency] = None

    def dependencies(self, task: str) -> tuple[str, ...]:
        """Return dependency names for a task."""

        return tuple(self._dependencies[task])

    def topological_sort(self) -> list[Task]:
        """Return tasks in deterministic dependency-first order."""

        indegree = {
            name: len(dependencies)
            for name, dependencies in self._dependencies.items()
        }
        dependents = {name: [] for name in self._nodes}
        for task, dependencies in self._dependencies.items():
            for dependency in dependencies:
                dependents[dependency].append(task)

        ready = deque(name for name, degree in indegree.items() if degree == 0)
        ordered: list[Task] = []
        while ready:
            name = ready.popleft()
            ordered.append(self._nodes[name])
            for dependent in dependents[name]:
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    ready.append(dependent)

        if len(ordered) != len(self._nodes):
            cycle = [name for name, degree in indegree.items() if degree]
            raise CycleError(f"Cycle detected involving: {', '.join(cycle)}")
        return ordered


def build_dag(tasks: dict[str, Task]) -> DAG:
    """Build and validate a DAG from registered tasks."""

    dag = DAG()
    for task in tasks.values():
        dag.add_node(task)

    for task in tasks.values():
        for dependency in task.depends:
            if tasks.get(dependency.name) is not dependency:
                raise UnknownDependencyError(
                    f"Task {task.name!r} depends on unknown task {dependency.name!r}"
                )
            dag.add_edge(dependency.name, task.name)
    return dag
