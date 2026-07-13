import pytest

from acyro import Task, TaskStatus, clear_registry, get_tasks, task


def test_task_decorator_registers_function_as_task() -> None:
    clear_registry()

    @task
    def download() -> str:
        return "data"

    assert isinstance(download, Task)
    assert download.name == "download"
    assert download.func() == "data"
    assert download.depends == ()
    assert download.status is TaskStatus.PENDING
    assert download.metadata["module"] == __name__
    assert download.metadata["qualname"].endswith("download")
    assert get_tasks() == {"download": download}


def test_task_decorator_accepts_dependencies() -> None:
    clear_registry()

    @task
    def download() -> None:
        pass

    @task(depends=[download])
    def train() -> None:
        pass

    assert train.depends == (download,)
    assert get_tasks() == {"download": download, "train": train}


def test_task_decorator_accepts_file_inputs_and_outputs() -> None:
    clear_registry()

    @task(inputs=["src/**/*.py"], outputs=["dist/report.json"])
    def build() -> None:
        pass

    assert build.inputs == ("src/**/*.py",)
    assert build.outputs == ("dist/report.json",)


def test_task_decorator_rejects_glob_outputs() -> None:
    clear_registry()

    with pytest.raises(ValueError, match="outputs must be explicit file paths"):

        @task(outputs=["dist/*.json"])
        def build() -> None:
            pass


def test_clear_registry_removes_registered_tasks() -> None:
    clear_registry()

    @task
    def download() -> None:
        pass

    assert get_tasks()
    clear_registry()
    assert get_tasks() == {}


def test_task_decorator_rejects_duplicate_names() -> None:
    clear_registry()

    @task(name="build")
    def first() -> None:
        pass

    with pytest.raises(ValueError, match="Task 'build' is already registered"):

        @task(name="build")
        def second() -> None:
            pass
