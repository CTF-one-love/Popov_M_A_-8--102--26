import copy
import json
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from lab1.errors import FormatError, SchemaError
from lab1.parser import parse_submission
from lab1.validation import validate_submission


def test_valid_and_unchanged(valid_record: dict[str, object]) -> None:
    original = copy.deepcopy(valid_record)
    submission = validate_submission(valid_record)
    assert valid_record == original
    assert submission.timestamp == datetime(2026, 1, 1, 9, tzinfo=UTC)
    assert submission.text == original["text"]
    assert submission.code == original["code"]
    assert parse_submission(json.dumps(valid_record)) == submission
    valid_record["ai_declaration"] = {"used": True, "details": "changed"}
    assert submission.ai_declaration.used is False
    with pytest.raises(FrozenInstanceError):
        setattr(submission, "text", "changed")  # noqa: B010
    with pytest.raises(FrozenInstanceError):
        setattr(submission.ai_declaration, "details", "changed")  # noqa: B010


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("student_id", "  ", "student_id"),
        ("submission_id", "", "submission_id"),
        ("assignment_id", None, "assignment_id"),
        ("student_id", 1, "student_id"),
        ("timestamp", "bad", "timestamp"),
        ("timestamp", "2026-01-01T12:00:00", "timestamp"),
        ("timestamp", "2026-02-30T12:00:00Z", "timestamp"),
        ("timestamp", 123, "timestamp"),
        ("timestamp", "0001-01-01T00:00:00+01:00", "timestamp"),
        ("text", [], "text"),
        ("code", True, "code"),
        ("text", "\ud800", "text"),
        ("extra", "unexpected", "extra"),
        ("ai_declaration", None, "ai_declaration"),
        ("ai_declaration", {"used": 1, "details": ""}, "ai_declaration.used"),
        ("ai_declaration", {"used": False, "details": 1}, "ai_declaration.details"),
        ("ai_declaration", {"used": False}, "ai_declaration.details"),
        (
            "ai_declaration",
            {"used": False, "details": "", "extra": 1},
            "ai_declaration.extra",
        ),
    ],
)
def test_schema_error(
    valid_record: dict[str, object], field: str, value: object, expected: str
) -> None:
    valid_record[field] = value
    original = copy.deepcopy(valid_record)
    with pytest.raises(SchemaError) as caught:
        validate_submission(valid_record)
    assert caught.value.code == "schema_error"
    assert caught.value.field == expected
    assert caught.value.message
    assert valid_record == original


@pytest.mark.parametrize(
    "field",
    [
        "submission_id",
        "student_id",
        "assignment_id",
        "timestamp",
        "text",
        "code",
        "ai_declaration",
    ],
)
def test_required_field(valid_record: dict[str, object], field: str) -> None:
    del valid_record[field]
    with pytest.raises(SchemaError) as caught:
        validate_submission(valid_record)
    assert caught.value.field == field


@pytest.mark.parametrize("line", ["{", "", "NaN", '{"x": 1, "x": 2}'])
def test_format_error(line: str) -> None:
    with pytest.raises(FormatError) as caught:
        parse_submission(line)
    assert caught.value.code == "format_error"
    assert caught.value.field == "$"


@pytest.mark.parametrize("line", ["[]", "null", "42", '"hello"'])
def test_valid_json_wrong_schema(line: str) -> None:
    with pytest.raises(SchemaError):
        parse_submission(line)


def test_empty_ai_explanation_allowed(valid_record: dict[str, object]) -> None:
    valid_record["ai_declaration"] = {"used": True, "details": "  "}
    submission = validate_submission(valid_record)
    assert submission.ai_declaration.used is True
    assert submission.ai_declaration.details == "  "
