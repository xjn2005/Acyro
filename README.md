# Acyro

[![PyPI](https://img.shields.io/pypi/v/acyro.svg?cacheSeconds=300)](https://pypi.org/project/acyro/)
[![Python](https://img.shields.io/pypi/pyversions/acyro.svg)](https://pypi.org/project/acyro/)
[![CI](https://github.com/xjn2005/Acyro/actions/workflows/ci.yml/badge.svg)](https://github.com/xjn2005/Acyro/actions/workflows/ci.yml)
[![License](https://img.shields.io/pypi/l/acyro.svg)](https://github.com/xjn2005/Acyro/blob/main/LICENSE)

**English** | [简体中文](https://github.com/xjn2005/Acyro/blob/main/README.zh-CN.md)

A small, local, Python-native DAG task runner with deterministic execution and
content-aware JSON caching.

## Install

```bash
pip install acyro
```

Requires Python 3.12 or newer.

## Quick start

```python
from pathlib import Path

from acyro import run, task


@task(inputs=["data/*.txt"], outputs=["build/combined.txt"])
def combine() -> None:
    Path("build").mkdir(exist_ok=True)
    content = "\n".join(path.read_text() for path in Path("data").glob("*.txt"))
    Path("build/combined.txt").write_text(content)


@task(depends=[combine], outputs=["dist/report.txt"])
def report() -> None:
    Path("dist").mkdir(exist_ok=True)
    Path("dist/report.txt").write_text(Path("build/combined.txt").read_text())


run()
```

`run()` executes tasks in dependency order. Later runs mark unchanged tasks as
`SKIPPED`.

## CLI

Put tasks in a Python file, then run or inspect the graph:

```bash
acyro run examples/acyrofile.py
acyro graph examples/acyrofile.py
```

## Cache

Successful tasks are cached under `.acyro/cache`. Fingerprints include task
metadata, source code, input contents, output contents, and dependency
fingerprints. Changing an input or dependency invalidates downstream tasks;
deleting or modifying an output reruns its task.

Input declarations accept explicit files and Glob patterns. Output declarations
must be explicit file paths. Paths are resolved from the current working
directory, and file contents are hashed with SHA-256. Missing inputs and outputs
raise clear errors without replacing the last successful cache record.

Tasks without `inputs` or `outputs` retain the original source- and
dependency-based cache behavior. Use `run(cache_dir=...)` to choose another
cache directory.

Acyro is intentionally serial and local. It has no async runtime, distributed
workers, database, retries, or pluggable cache backends.

## Development

```bash
uv sync --extra dev
uv run pytest -q
uv run ruff check .
uv build
```

Licensed under the [MIT License](https://github.com/xjn2005/Acyro/blob/main/LICENSE).
