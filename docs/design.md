# Acyro Design

## Why Acyro Exists

Acyro is a small Python-native workflow build system for local, repeatable task
graphs. It is for projects where a developer wants Make-like dependency
execution without leaving Python:

```python
from acyro import run, task

@task
def download():
    pass

@task(depends=[download])
def train():
    pass

run()
```

The v0.1 goal is deliberately narrow: define tasks as Python functions, build a
DAG, run dependencies in order, detect cycles, and skip work that has not
changed.

Acyro is not a scheduler, orchestrator, queue, or platform. It should feel
closer to Make or Ninja than Airflow.

## Comparison

Make is simple, local, file-oriented, and excellent at incremental builds. Acyro
borrows its dependency-first execution model and "skip unchanged work" spirit,
but replaces Makefiles with Python functions.

CMake generates build systems and shines for cross-platform native builds.
Acyro is not a generator and does not try to model compilers, toolchains, or
platform-specific build targets.

Ninja is fast, explicit, and intentionally minimal. Acyro borrows that bias
toward a small execution core, clear graph behavior, and predictable output.

Airflow is a distributed workflow orchestration platform with scheduling,
workers, persistence, retries, backfills, web UI, and operational concepts.
Acyro avoids that entire class of features in v0.1. Local execution and local
cache files are enough.

## Architecture

Acyro has five small parts:

1. `task.py`: the `@task` decorator, task metadata, dependency declarations, and
   a registry for tasks defined in user code.
2. `dag.py`: node and edge handling, topological sorting, and cycle detection.
3. `cache.py`: file-based cache records keyed by task identity, task code, and
   dependency metadata.
4. `executor.py`: dependency-order execution, status updates, failure handling,
   cache checks, and progress logs.
5. `cli.py`: `acyro run` and `acyro graph`.

The public API should stay tiny:

```python
from acyro import run, task
```

The CLI should import the user's workflow module, let decorators register tasks,
then execute or print the graph. The Python API should use the same engine so
CLI and in-process behavior do not drift.

## Data Flow

1. User imports `task` and decorates Python functions.
2. Each decorator call creates task metadata and stores it in the active
   registry.
3. `run()` builds a DAG from the registry.
4. The DAG engine topologically sorts tasks and raises on cycles.
5. The executor walks the sorted tasks.
6. For each task, the cache compares the current task fingerprint with the last
   successful cache record.
7. Unchanged tasks are skipped. Changed or uncached tasks run.
8. Successful tasks write cache records. Failed tasks stop execution and keep
   stale cache records untouched.

## Cache Design

The v0.1 cache is a local directory, `.acyro/cache`, containing JSON
records. A task fingerprint should include:

- task name
- function module and qualified name
- normalized dependency names
- source code when available

This is intentionally metadata/code caching, not full file input/output
tracking. Users who need file-level invalidation can get it later through a
small explicit API, but v0.1 should not guess filesystem dependencies.

## CLI Design

`acyro run` executes the registered workflow and prints compact progress:

```text
[run] download
[skip] train
[fail] evaluate: ValueError(...)
```

`acyro graph` prints a simple text graph, enough to debug dependency shape
without adding Graphviz or a UI:

```text
download -> train
train -> evaluate
```

## Design Trade-Offs

Acyro chooses a decorator registry over a declarative config file because the
main value is Python-native workflows.

Acyro chooses local JSON cache files over SQLite because v0.1 does not need
queries, concurrent writers, or cross-process coordination.

Acyro chooses serial execution over parallel execution because correctness,
failure behavior, and cache semantics should be boring first. Parallelism can be
added later without changing the task API if the DAG boundaries stay clean.

Acyro chooses explicit dependencies over automatic dependency discovery because
implicit discovery is fragile and surprising in Python.

Acyro chooses plain CLI output over rich terminal UI because the early user need
is clarity, not presentation.

## Non-Goals

Acyro v0.1 will not include:

- distributed execution
- web UI
- database-backed state
- async scheduler
- cron or interval scheduling
- workers or queues
- retries and backfills
- automatic file dependency scanning
- plugin systems

## Step Plan

1. Project structure and this design document.
2. Task abstraction.
3. DAG engine.
4. Executor.
5. Cache.
6. CLI.
7. README and examples.

Each step should leave a small, tested slice behind. If a feature does not serve
the v0.1 goal, it waits.
