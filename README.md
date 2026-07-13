# Acyro

[![PyPI](https://img.shields.io/pypi/v/acyro.svg?cacheSeconds=300)](https://pypi.org/project/acyro/)
[![Python](https://img.shields.io/pypi/pyversions/acyro.svg)](https://pypi.org/project/acyro/)
[![CI](https://github.com/xjn2005/Acyro/actions/workflows/ci.yml/badge.svg)](https://github.com/xjn2005/Acyro/actions/workflows/ci.yml)
[![License](https://img.shields.io/pypi/l/acyro.svg)](https://github.com/xjn2005/Acyro/blob/main/LICENSE)

**English** | [简体中文](https://github.com/xjn2005/Acyro/blob/main/README.zh-CN.md)

A small, local, Python-native DAG task runner with deterministic execution and
JSON caching.

## Install

```bash
pip install acyro
```

Requires Python 3.12 or newer.

## Quick start

```python
from acyro import run, task


@task
def download() -> None:
    print("download")


@task(depends=[download])
def build() -> None:
    print("build")


run()
```

`run()` executes tasks in dependency order. Later runs skip unchanged tasks.

## CLI

Put tasks in a Python file, then run or inspect the graph:

```bash
acyro run examples/acyrofile.py
acyro graph examples/acyrofile.py
```

## Cache

Successful tasks are cached under `.acyro/cache`. Fingerprints include task
metadata, source code, and dependency fingerprints, so dependency changes
invalidate downstream tasks. Use `run(cache_dir=...)` to choose another cache
directory.

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
