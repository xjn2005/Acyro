import pytest

from acyro.dag import DAG, build_dag
from acyro.exceptions import CycleError, UnknownDependencyError
from acyro.task import Task


def make_task(name: str, *depends: Task) -> Task:
    return Task(name=name, func=lambda: None, depends=depends)


def test_dag_adds_nodes_edges_and_queries_dependencies() -> None:
    first = make_task("first")
    second = make_task("second")
    dag = DAG()

    dag.add_node(first)
    dag.add_node(second)
    dag.add_edge("first", "second")

    assert dag.nodes == (first, second)
    assert dag.dependencies("second") == ("first",)


def test_topological_sort_orders_linear_dependencies() -> None:
    first = make_task("first")
    second = make_task("second", first)
    third = make_task("third", second)

    dag = build_dag({task.name: task for task in (first, second, third)})

    assert dag.topological_sort() == [first, second, third]


def test_topological_sort_orders_multiple_dependencies_before_task() -> None:
    fetch = make_task("fetch")
    clean = make_task("clean")
    train = make_task("train", fetch, clean)

    dag = build_dag({task.name: task for task in (fetch, clean, train)})

    assert dag.topological_sort() == [fetch, clean, train]


def test_topological_sort_is_deterministic_for_independent_tasks() -> None:
    first = make_task("first")
    second = make_task("second")
    third = make_task("third")
    dag = build_dag({task.name: task for task in (first, second, third)})

    assert dag.topological_sort() == [first, second, third]
    assert dag.topological_sort() == [first, second, third]


def test_build_dag_rejects_missing_dependency() -> None:
    missing = make_task("missing")
    task = make_task("task", missing)

    with pytest.raises(
        UnknownDependencyError,
        match="Task 'task' depends on unknown task 'missing'",
    ):
        build_dag({"task": task})


def test_topological_sort_detects_cycle() -> None:
    first = make_task("first")
    second = make_task("second", first)
    third = make_task("third", second)
    first.depends = (third,)

    with pytest.raises(CycleError, match="first.*second.*third"):
        dag = build_dag({task.name: task for task in (first, second, third)})
        dag.topological_sort()
