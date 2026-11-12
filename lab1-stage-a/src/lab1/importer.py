"""Файловый адаптер массового приёма JSONL."""

from dataclasses import dataclass, field
from pathlib import Path

from lab1.errors import FormatError, SubmissionError
from lab1.intake import SubmissionService
from lab1.models import IntakeStatus


@dataclass(slots=True)
class ImportReport:
    """Счётчики приёма и диагностика отклонённых строк."""

    accepted: int = 0
    duplicate: int = 0
    errors: list[dict[str, str | int]] = field(default_factory=list)


def import_file(path: Path, service: SubmissionService) -> ImportReport:
    """Импортировать файл построчно, не прерываясь на отклонённых сдачах.

    Args:
        path: Путь к JSONL в UTF-8.
        service: Сервис с хранилищем на время импорта.

    Returns:
        Счётчики и ошибки с физическими номерами строк от единицы.

    Raises:
        OSError: Если файл невозможно открыть или прочитать.
    """
    report = ImportReport()
    # Бинарное чтение позволяет изолировать даже строку с битым UTF-8.
    with path.open("rb") as stream:
        for number, raw in enumerate(stream, start=1):
            try:
                try:
                    line = raw.decode("utf-8")
                except UnicodeDecodeError as exc:
                    raise FormatError("Строка не является UTF-8.") from exc
                result = service.accept_json(line)
            except SubmissionError as exc:
                report.errors.append({"line": number, **exc.as_dict()})
                continue
            if result.status == IntakeStatus.ACCEPTED:
                report.accepted += 1
            else:
                report.duplicate += 1
    return report
