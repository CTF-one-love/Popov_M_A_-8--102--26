"""Неизменяемые модели принятых сдач и результата приёма."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


@dataclass(frozen=True, slots=True)
class AIDeclaration:
    """Самодекларация студента, а не доказательство происхождения работы.

    Attributes:
        used: Применял ли студент инструменты ИИ.
        details: Пояснение студента; его полнота оценивается отдельно.
    """

    used: bool
    details: str


@dataclass(frozen=True, slots=True)
class Submission:
    """Одна версия работы после проверки входного контракта.

    Создаётся валидатором. Исходные text и code сохраняются без изменений;
    timestamp представлен моментом времени с часовым поясом UTC.
    """

    submission_id: str
    student_id: str
    assignment_id: str
    timestamp: datetime
    text: str
    code: str
    ai_declaration: AIDeclaration


class IntakeStatus(StrEnum):
    """Успешные исходы приёма; конфликт представлен исключением."""

    ACCEPTED = "accepted"
    DUPLICATE = "duplicate"


@dataclass(frozen=True, slots=True)
class IntakeResult:
    """Результат приёма с канонической сохранённой сдачей и её хешем."""

    status: IntakeStatus
    submission: Submission
    content_hash: str
