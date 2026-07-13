"""Minimal Acyro workflow."""

from acyro import task


@task
def download() -> None:
    print("download")


@task(depends=[download])
def build() -> None:
    print("build")
