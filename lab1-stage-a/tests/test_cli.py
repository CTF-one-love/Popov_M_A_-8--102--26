import json
import subprocess
import sys
from pathlib import Path

import pytest

from lab1.cli import main

DATA = Path(__file__).resolve().parents[1] / "data"


def test_cli_valid(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["import", str(DATA / "submissions.jsonl")]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report == {"accepted": 2, "duplicate": 1, "errors": []}


def test_cli_invalid(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["import", str(DATA / "invalid_submissions.jsonl")]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["accepted"] == 2
    assert report["duplicate"] == 1
    assert [(e["line"], e["code"]) for e in report["errors"]] == [
        (2, "format_error"),
        (3, "schema_error"),
        (4, "conflict"),
        (5, "schema_error"),
        (6, "schema_error"),
    ]


def test_cli_missing_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["import", str(tmp_path / "missing.jsonl")]) == 2
    captured = capsys.readouterr()
    assert not captured.out
    assert "файл" in captured.err


def test_cli_usage_error() -> None:
    with pytest.raises(SystemExit) as caught:
        main([])
    assert caught.value.code == 2


def test_module_entrypoint() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "lab1", "import", str(DATA / "submissions.jsonl")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["accepted"] == 2
