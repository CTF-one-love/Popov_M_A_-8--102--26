"""Ошибки предметной области, независимые от CLI и HTTP."""


class SubmissionError(Exception):
    """Диагностика отклонённой сдачи без раскрытия её содержимого."""

    def __init__(self, code: str, field: str, message: str) -> None:
        """Сохранить машиночитаемый код, поле и пояснение для пользователя."""
        super().__init__(message)
        self.code = code
        self.field = field
        self.message = message

    def as_dict(self) -> dict[str, str]:
        """Вернуть представление ошибки для внешнего интерфейса."""
        return {"code": self.code, "field": self.field, "message": self.message}


class FormatError(SubmissionError):
    """Входную строку невозможно разобрать как однозначный JSON."""

    def __init__(self, message: str) -> None:
        """Сформировать ошибку формата всей строки."""
        super().__init__("format_error", "$", message)


class SchemaError(SubmissionError):
    """JSON не соответствует контракту сдачи."""

    def __init__(self, field: str, message: str) -> None:
        """Указать нарушенное поле схемы."""
        super().__init__("schema_error", field, message)


class ConflictError(SubmissionError):
    """Идентификатор уже закреплён за другим содержимым сдачи."""

    def __init__(self) -> None:
        """Сообщить о конфликте без раскрытия сохранённой работы."""
        super().__init__(
            "conflict", "submission_id", "Идентификатор уже занят другой сдачей."
        )
