# Acyro Design

## Purpose

Acyro is a small Python-native build and task runner for local, repeatable DAGs.
It provides Make-like dependency execution without requiring a separate
configuration language:

```python
from acyro import run, task


@task(inputs=["data/*.csv"], outputs=["build/merged.csv"])
def merge() -> None:
    ...


@task(depends=[merge])
def report() -> None:
    ...


run()
```

The v0.2 scope is deliberately narrow: define tasks as Python functions, build
a DAG, run dependencies serially, detect cycles, and skip work whose code,
dependencies, inputs, and outputs have not changed. Acyro is closer to Make or
Ninja than to a scheduler or orchestration platform.

## Architecture

Acyro has five small parts:

1. `task.py` defines `Task`, `@task`, file declarations, statuses, and the task
   registry.
2. `dag.py` validates dependencies, stores edges, sorts tasks, and detects
   cycles.
3. `cache.py` computes fingerprints and stores successful JSON cache records.
4. `executor.py` runs tasks in dependency order and updates their statuses.
5. `cli.py` imports workflow files and provides `acyro run` and `acyro graph`.

The CLI and Python API use the same registry, DAG, executor, and cache. The
public API remains intentionally small:

```python
from acyro import run, task
```

## Execution Flow

1. Decorated functions register `Task` objects.
2. `run()` builds and topologically sorts the task DAG.
3. The cache validates each task's current fingerprint.
4. A matching task is marked `SKIPPED`; otherwise it runs.
5. A successful task validates its outputs and writes a cache record.
6. A failed task is marked `FAILED`, stops execution, and leaves its previous
   successful record untouched.

Execution is deterministic and serial. Independent tasks follow the stable
ordering provided by the DAG engine.

## File-Aware Cache

The default cache lives in `.acyro/cache` and contains one JSON record per task.
`run(cache_dir=...)` may select another directory. A fingerprint includes:

- task name, module, and qualified name
- function source code when available
- dependency fingerprints
- declared input paths and SHA-256 content hashes
- declared output paths and SHA-256 content hashes

Inputs may be explicit file paths or Glob patterns. Outputs must be explicit
file paths. All paths resolve from the current working directory. Plain
directories are not expanded automatically; recursive matching must be explicit,
for example `src/**/*.py`.

A missing explicit input or a Glob with no matches raises
`InputNotFoundError` before execution. After a function returns successfully,
every declared output must exist or `OutputNotFoundError` is raised. A missing
or externally modified output invalidates its task. Because output hashes are
part of task fingerprints, dependency output changes also invalidate downstream
tasks.

Tasks without `inputs` or `outputs` retain the v0.1 source- and
dependency-based behavior. Missing or corrupted JSON records are ordinary cache
misses.

## Design Choices

Acyro uses decorators instead of a declarative config file because its main
value is Python-native workflows. It uses local JSON instead of SQLite because
the current scope needs neither queries nor concurrent writers. Dependencies and
file declarations are explicit so cache behavior remains predictable.

## Non-Goals

Acyro v0.2 does not include:

- target task selection
- parallel, async, or distributed execution
- workers, queues, scheduling, retries, or backfills
- database storage or configurable cache backends
- automatic directory recursion or dependency discovery
- mtime-based cache shortcuts
- web UI or plugin systems

Future additions should preserve the small public API and local execution model.
