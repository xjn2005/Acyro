# Acyro

[![PyPI](https://img.shields.io/pypi/v/acyro.svg?cacheSeconds=300)](https://pypi.org/project/acyro/)
[![Python](https://img.shields.io/pypi/pyversions/acyro.svg)](https://pypi.org/project/acyro/)
[![CI](https://github.com/xjn2005/Acyro/actions/workflows/ci.yml/badge.svg)](https://github.com/xjn2005/Acyro/actions/workflows/ci.yml)
[![License](https://img.shields.io/pypi/l/acyro.svg)](https://github.com/xjn2005/Acyro/blob/main/LICENSE)

[English](https://github.com/xjn2005/Acyro#readme) | **简体中文**

Acyro 是一个小型、本地、Python 原生的 DAG 任务运行器，提供确定性的依赖执行与 JSON 缓存。

## 安装

```bash
pip install acyro
```

需要 Python 3.12 或更高版本。

## 快速开始

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

`run()` 会按依赖顺序执行任务。再次运行时，未发生变化的任务会被跳过。

## CLI

将任务放入 Python 文件后，可以直接运行或查看依赖图：

```bash
acyro run examples/acyrofile.py
acyro graph examples/acyrofile.py
```

## 缓存

成功的任务默认缓存在 `.acyro/cache`。任务指纹包含元数据、源代码和依赖指纹，因此依赖变化会使下游任务的缓存失效。可以通过 `run(cache_dir=...)` 指定其他缓存目录。

Acyro 坚持串行、本地的设计范围，不包含异步运行时、分布式 Worker、数据库、重试机制或可插拔缓存后端。

## 开发

```bash
uv sync --extra dev
uv run pytest -q
uv run ruff check .
uv build
```

本项目采用 [MIT License](https://github.com/xjn2005/Acyro/blob/main/LICENSE)。
