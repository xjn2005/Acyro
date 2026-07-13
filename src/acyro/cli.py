"""Acyro command-line interface."""

import argparse
import importlib.util
from pathlib import Path

from acyro.dag import build_dag
from acyro.executor import run
from acyro.task import TaskStatus, clear_registry, get_tasks


def _load_workflow(path: Path) -> None:
    clear_registry()
    spec = importlib.util.spec_from_file_location("_acyro_workflow", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load workflow: {path}")
    spec.loader.exec_module(importlib.util.module_from_spec(spec))


def main(argv: list[str] | None = None) -> int:
    """Run the Acyro command-line interface."""

    parser = argparse.ArgumentParser(prog="acyro")
    commands = parser.add_subparsers(dest="command", required=True)
    graph_parser = commands.add_parser("graph", help="print the task graph")
    graph_parser.add_argument("workflow", type=Path)
    run_parser = commands.add_parser("run", help="run registered tasks")
    run_parser.add_argument("workflow", type=Path)
    run_parser.add_argument(
        "--cache-dir", type=Path, default=Path(".acyro/cache")
    )
    args = parser.parse_args(argv)

    _load_workflow(args.workflow)
    dag = build_dag(get_tasks())
    ordered = dag.topological_sort()
    if args.command == "run":
        run(get_tasks(), cache_dir=args.cache_dir)
        for task in ordered:
            action = "skip" if task.status is TaskStatus.SKIPPED else "run"
            print(f"[{action}] {task.name}")
        return 0

    edges = [
        (dependency, task.name)
        for task in dag.nodes
        for dependency in dag.dependencies(task.name)
    ]
    for dependency, task in edges:
        print(f"{dependency} -> {task}")
    connected = {name for edge in edges for name in edge}
    for task in dag.nodes:
        if task.name not in connected:
            print(task.name)
    return 0
