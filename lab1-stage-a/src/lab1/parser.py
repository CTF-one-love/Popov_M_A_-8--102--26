"""Разбор JSON без неявной потери полей и данных."""

import json
from typing import NoReturn

from lab1.errors import FormatError
from lab1.models import Submission
from lab1.validation import validate_submission


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise FormatError("Повторяющийся ключ JSON.")
        result[key] = value
    return result


def _reject_constant(value: str) -> NoReturn:
    raise FormatError("Нестандартное числовое значение JSON.")


def parse_submission(line: str) -> Submission:
    """Преобразовать одну строку JSON в валидированную сдачу.

    Raises:
        FormatError: Если JSON повреждён или неоднозначен.
        SchemaError: Если разобранный JSON нарушает схему сдачи.
    """
    try:
        raw = json.loads(
            line, object_pairs_hook=_unique_object, parse_constant=_reject_constant
        )
    except (ValueError, RecursionError) as exc:
        raise FormatError("Некорректная строка JSON.") from exc
    return validate_submission(raw)
