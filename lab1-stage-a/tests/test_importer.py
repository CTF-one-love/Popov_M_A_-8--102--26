import io
import json
from pathlib import Path

import pytest

from lab1.importer import import_file
from lab1.intake import SubmissionService
from lab1.models import IntakeResult
from lab1.repository import InMemorySubmissionRepository


def test_mixed_import(tmp_path: Path, valid_record: dict[str, object]) -> None:
    path = tmp_path / "mixed.jsonl"
    first = json.dumps(valid_record).encode()
    conflict = json.dumps({**valid_record, "text": "other"}).encode()
    second = json.dumps({**valid_record, "submission_id": "demo-002"}).encode()
    path.write_bytes(b"\n".join([first, b"{", first, conflict, b"\xff", second]))
    repository = InMemorySubmissionRepository()
    report = import_file(path, SubmissionService(repository))
    assert (report.accepted, report.duplicate, len(repository)) == (2, 1, 2)
    assert [(e["line"], e["code"]) for e in report.errors] == [
        (2, "format_error"),
        (4, "conflict"),
        (5, "format_error"),
    ]
    assert all(set(e) == {"line", "code", "field", "message"} for e in report.errors)


def test_resource_closed_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    class BrokenService(SubmissionService):
        def accept_json(self, line: str) -> IntakeResult:
            raise RuntimeError("Unexpected failure")

    stream = io.BytesIO(b"{}\n")
    monkeypatch.setattr(Path, "open", lambda *args, **kwargs: stream)
    with pytest.raises(RuntimeError, match="Unexpected failure"):
        import_file(
            Path("synthetic.jsonl"), BrokenService(InMemorySubmissionRepository())
        )
    assert stream.closed


def test_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.jsonl"
    path.touch()
    report = import_file(path, SubmissionService(InMemorySubmissionRepository()))
    assert (report.accepted, report.duplicate, report.errors) == (0, 0, [])
