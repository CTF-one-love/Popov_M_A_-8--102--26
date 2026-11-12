"""Проверка структуры внешних данных и построение доменной модели."""

from datetime import UTC, datetime
from typing import cast

from lab1.errors import SchemaError
from lab1.models import AIDeclaration, Submission

_SUBMISSION_FIELDS = (
    "submission_id",
    "student_id",
    "assignment_id",
    "timestamp",
    "text",
    "code",
    "ai_declaration",
)
_DECLARATION_FIELDS = ("used", "details")


def _object(
    value: object, fields: tuple[str, ...], prefix: str = ""
) -> dict[str, object]:
    if not isinstance(value, dict):
        raise SchemaError(prefix.rstrip(".") or "$", "Ожидается объект JSON.")
    for key in fields:
        if key not in value:
            raise SchemaError(f"{prefix}{key}", "Обязательное поле отсутствует.")
    for key in value:
        if not isinstance(key, str) or key not in fields:
            field = (
                f"{prefix}{key}" if isinstance(key, str) else prefix.rstrip(".") or "$"
            )
            raise SchemaError(field, "Неизвестное поле.")
    return cast(dict[str, object], value)


def _string(value: object, field: str, *, nonempty: bool = False) -> str:
    if not isinstance(value, str):
        raise SchemaError(field, "Ожидается строка.")
    if nonempty and not value.strip():
        raise SchemaError(field, "Поле не должно быть пустым.")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise SchemaError(field, "Строка содержит недопустимый Unicode.") from exc
    return value


def _timestamp(value: object) -> datetime:
    raw = _string(value, "timestamp")
    try:
        timestamp = datetime.fromisoformat(raw)
        if timestamp.utcoffset() is None:
            raise ValueError("timezone required")
        return timestamp.astimezone(UTC)
    except (ValueError, OverflowError) as exc:
        raise SchemaError(
            "timestamp", "Ожидается дата и время ISO 8601 с часовым поясом."
        ) from exc


def _declaration(value: object) -> AIDeclaration:
    data = _object(value, _DECLARATION_FIELDS, "ai_declaration.")
    used = data["used"]
    if not isinstance(used, bool):
        raise SchemaError("ai_declaration.used", "Ожидается логическое значение.")
    # Полнота пояснения — задача анализа, а не основание отклонять сдачу.
    return AIDeclaration(used, _string(data["details"], "ai_declaration.details"))


def validate_submission(value: object) -> Submission:
    """Проверить внешний объект и создать неизменяемую сдачу.

    Args:
        value: Декодированный JSON или словарь от вызывающего кода.

    Returns:
        Валидированная сдача; входной объект остаётся неизменным.

    Raises:
        SchemaError: Если отсутствует поле или нарушен его контракт.
    """
    data = _object(value, _SUBMISSION_FIELDS)
    return Submission(
        submission_id=_string(data["submission_id"], "submission_id", nonempty=True),
        student_id=_string(data["student_id"], "student_id", nonempty=True),
        assignment_id=_string(data["assignment_id"], "assignment_id", nonempty=True),
        timestamp=_timestamp(data["timestamp"]),
        text=_string(data["text"], "text"),
        code=_string(data["code"], "code"),
        ai_declaration=_declaration(data["ai_declaration"]),
    )
