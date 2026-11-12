"""Сценарий приёма: проверка, идентификация и сохранение сдачи."""

from lab1.errors import ConflictError
from lab1.hashing import submission_hash
from lab1.models import IntakeResult, IntakeStatus, Submission
from lab1.parser import parse_submission
from lab1.repository import StoredSubmission, SubmissionRepository
from lab1.validation import validate_submission


class SubmissionService:
    """Принимает сдачи независимо от формата внешнего интерфейса."""

    def __init__(self, repository: SubmissionRepository) -> None:
        """Получить хранилище через композицию."""
        self._repository = repository

    def accept(self, value: object) -> IntakeResult:
        """Принять внешний объект после проверки схемы.

        Raises:
            SchemaError: Если объект не соответствует контракту.
            ConflictError: Если ID занят другой версией.
        """
        return self._accept_validated(validate_submission(value))

    def accept_json(self, line: str) -> IntakeResult:
        """Принять сдачу из одной строки JSON.

        Raises:
            FormatError: Если JSON невозможно разобрать.
            SchemaError: Если нарушена схема.
            ConflictError: Если ID занят другой версией.
        """
        return self._accept_validated(parse_submission(line))

    def _accept_validated(self, submission: Submission) -> IntakeResult:
        content_hash = submission_hash(submission)
        existing = self._repository.get(submission.submission_id)
        if existing is not None:
            if existing.content_hash != content_hash:
                raise ConflictError()
            return IntakeResult(
                IntakeStatus.DUPLICATE, existing.submission, existing.content_hash
            )
        self._repository.add(StoredSubmission(submission, content_hash))
        return IntakeResult(IntakeStatus.ACCEPTED, submission, content_hash)
