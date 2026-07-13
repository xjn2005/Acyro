# Acyro

Acyro is a small, local DAG task runner for Python. It executes decorated
functions in dependency order and skips unchanged work using a local JSON cache.

## Install

```bash
pip install acyro
```

Until the first PyPI release, install a checkout with `uv sync --extra dev`.

## Python API

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

`run()` caches successful tasks under `.acyro/cache`. A task runs again when
its metadata, source code, or any dependency fingerprint changes. Pass
`run(cache_dir=...)` to use another directory.

## CLI

Put tasks in a Python file, then run or inspect them:

```bash
acyro graph examples/acyrofile.py
acyro run examples/acyrofile.py
```

Example graph output:

```text
download -> build
```

## Scope

Acyro v0.1 is intentionally serial and local. It has no scheduler, distributed
workers, async runtime, database, retries, or pluggable cache backends.

## Development

```bash
uv sync --extra dev
uv run pytest -q
uv run ruff check .
uv build
```

See [publishing instructions](docs/publishing.md) for the one-time GitHub and
PyPI setup.
