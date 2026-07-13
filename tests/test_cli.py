from pathlib import Path

from acyro import cli


def test_graph_prints_dependency_edges(tmp_path: Path, capsys) -> None:
    workflow = tmp_path / "workflow.py"
    workflow.write_text(
        "from acyro import task\n"
        "@task\n"
        "def first(): pass\n"
        "@task(depends=[first])\n"
        "def second(): pass\n",
        encoding="utf-8",
    )

    assert cli.main(["graph", str(workflow)]) == 0
    assert capsys.readouterr().out == "first -> second\n"


def test_run_executes_workflow_and_reports_cache_hits(tmp_path: Path, capsys) -> None:
    workflow = tmp_path / "workflow.py"
    marker = tmp_path / "marker.txt"
    cache_dir = tmp_path / "cache"
    workflow.write_text(
        "from pathlib import Path\n"
        "from acyro import task\n"
        "@task\n"
        "def build():\n"
        f"    with Path({str(marker)!r}).open('a') as output:\n"
        "        output.write('x')\n",
        encoding="utf-8",
    )

    assert cli.main(
        ["run", str(workflow), "--cache-dir", str(cache_dir)]
    ) == 0
    assert capsys.readouterr().out == "[run] build\n"

    assert cli.main(
        ["run", str(workflow), "--cache-dir", str(cache_dir)]
    ) == 0
    assert capsys.readouterr().out == "[skip] build\n"
    assert marker.read_text(encoding="utf-8") == "x"
