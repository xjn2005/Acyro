# Acyro

[![PyPI](https://img.shields.io/pypi/v/acyro.svg?cacheSeconds=300)](https://pypi.org/project/acyro/)
[![Python](https://img.shields.io/pypi/pyversions/acyro.svg)](https://pypi.org/project/acyro/)
[![CI](https://github.com/xjn2005/Acyro/actions/workflows/ci.yml/badge.svg)](https://github.com/xjn2005/Acyro/actions/workflows/ci.yml)
[![License](https://img.shields.io/pypi/l/acyro.svg)](https://github.com/xjn2005/Acyro/blob/main/LICENSE)

[English](https://github.com/xjn2005/Acyro#readme) | **简体中文**

Acyro 是一个小型、本地、Python 原生的 DAG 任务运行器，提供确定性的依赖执行与内容感知 JSON 缓存。

## 安装

```bash
pip install acyro
```

需要 Python 3.12 或更高版本。

## 快速开始

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

`run()` 会按依赖顺序执行任务。再次运行时，未发生变化的任务会标记为 `SKIPPED`。

## CLI

将任务放入 Python 文件后，可以直接运行或查看依赖图：

```bash
acyro run examples/acyrofile.py
acyro graph examples/acyrofile.py
```

## 缓存

成功的任务默认缓存在 `.acyro/cache`。任务指纹包含元数据、源代码、输入内容、输出内容和依赖指纹。输入或依赖变化会使下游任务的缓存失效；输出被删除或修改时，对应任务会重新运行。

输入声明支持显式文件和 Glob 模式，输出声明只能使用显式文件路径。所有路径都相对于当前工作目录解析，文件内容使用 SHA-256 哈希。输入或输出缺失时，Acyro 会抛出清晰的错误，并保留上一次成功的缓存记录。

未声明 `inputs` 或 `outputs` 的任务会保留原有的源代码与依赖指纹缓存行为。可以通过 `run(cache_dir=...)` 指定其他缓存目录。

Acyro 坚持串行、本地的设计范围，不包含异步运行时、分布式 Worker、数据库、重试机制或可插拔缓存后端。

## 开发

```bash
uv sync --extra dev
uv run pytest -q
uv run ruff check .
uv build
```

本项目采用 [MIT License](https://github.com/xjn2005/Acyro/blob/main/LICENSE)。
