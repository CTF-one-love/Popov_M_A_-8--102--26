"""Контракт хранения и его реализация для одного процесса."""

from dataclasses import dataclass
from typing import Protocol

from lab1.errors import ConflictError
from lab1.models import Submission


@dataclass(frozen=True, slots=True)
class StoredSubmission:
    """Сохранённая версия работы и её содержательный отпечаток."""

    submission: Submission
    content_hash: str


class SubmissionRepository(Protocol):
    """Минимальный контракт, необходимый сервису приёма."""

    def get(self, submission_id: str) -> StoredSubmission | None:
        """Найти сохранённую версию по идентификатору."""
        ...

    def add(self, record: StoredSubmission) -> None:
        """Добавить новую версию, не перезаписывая существующую."""
        ...


class InMemorySubmissionRepository:
    """Хранение сдач на протяжении жизни экземпляра репозитория.

    Рассчитан на синхронное использование в одном процессе.
    """

    def __init__(self) -> None:
        """Создать пустое независимое хранилище."""
        self._records: dict[str, StoredSubmission] = {}

    def get(self, submission_id: str) -> StoredSubmission | None:
        """Вернуть ранее сохранённую запись или None."""
        return self._records.get(submission_id)

    def add(self, record: StoredSubmission) -> None:
        """Сохранить новую запись.

        Raises:
            ConflictError: Если идентификатор уже существует.
        """
        submission_id = record.submission.submission_id
        if submission_id in self._records:
            raise ConflictError()
        self._records[submission_id] = record

    def __len__(self) -> int:
        """Вернуть число сохранённых версий работ."""
        return len(self._records)
