import json

import pytest

from lab1.errors import ConflictError, SchemaError
from lab1.hashing import submission_hash
from lab1.intake import SubmissionService
from lab1.models import IntakeStatus
from lab1.repository import InMemorySubmissionRepository, StoredSubmission
from lab1.validation import validate_submission


def test_duplicate_returns_same_object(valid_record: dict[str, object]) -> None:
    repository = InMemorySubmissionRepository()
    service = SubmissionService(repository)
    first = service.accept(valid_record)
    reordered = dict(reversed(list(valid_record.items())))
    second = service.accept_json(json.dumps(reordered, indent=2))
    assert first.status == IntakeStatus.ACCEPTED
    assert second.status == IntakeStatus.DUPLICATE
    assert first.submission is second.submission
    assert first.content_hash == second.content_hash
    assert len(repository) == 1


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("text", "changed"),
        ("code", "changed"),
        ("student_id", "other-demo"),
        ("assignment_id", "other-lab"),
        ("timestamp", "2026-01-01T12:00:00Z"),
        ("ai_declaration", {"used": True, "details": "demo"}),
    ],
)
def test_conflict_never_overwrites(
    valid_record: dict[str, object], field: str, value: object
) -> None:
    repository = InMemorySubmissionRepository()
    service = SubmissionService(repository)
    accepted = service.accept(valid_record)
    valid_record[field] = value
    with pytest.raises(ConflictError) as caught:
        service.accept(valid_record)
    assert caught.value.code == "conflict"
    assert caught.value.field == "submission_id"
    assert repository.get(accepted.submission.submission_id) == StoredSubmission(
        accepted.submission, accepted.content_hash
    )
    assert len(repository) == 1


def test_new_id_is_new_version(valid_record: dict[str, object]) -> None:
    repository = InMemorySubmissionRepository()
    service = SubmissionService(repository)
    service.accept(valid_record)
    valid_record["submission_id"] = "demo-002"
    assert service.accept(valid_record).status == IntakeStatus.ACCEPTED
    assert len(repository) == 2


def test_invalid_direct_call_not_stored(valid_record: dict[str, object]) -> None:
    repository = InMemorySubmissionRepository()
    valid_record["student_id"] = ""
    with pytest.raises(SchemaError):
        SubmissionService(repository).accept(valid_record)
    assert len(repository) == 0


def test_equivalent_timestamp_hash(valid_record: dict[str, object]) -> None:
    first = validate_submission(valid_record)
    valid_record["timestamp"] = "2026-01-01T09:00:00Z"
    second = validate_submission(valid_record)
    assert submission_hash(first) == submission_hash(second)
    assert len(submission_hash(first)) == 64


def test_repository_rejects_overwrite(valid_record: dict[str, object]) -> None:
    repository = InMemorySubmissionRepository()
    submission = validate_submission(valid_record)
    record = StoredSubmission(submission, submission_hash(submission))
    repository.add(record)
    with pytest.raises(ConflictError):
        repository.add(record)
    assert repository.get(submission.submission_id) is record
