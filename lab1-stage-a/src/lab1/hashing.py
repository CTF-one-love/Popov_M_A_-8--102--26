"""Стабильный отпечаток содержимого валидированной сдачи."""

import hashlib
import json
from dataclasses import asdict

from lab1.models import Submission


def submission_hash(submission: Submission) -> str:
    """Вычислить SHA-256 канонического представления всех полей.

    Порядок ключей и пробелы JSON не влияют на хеш. В тексте, коде и
    декларации сохраняется каждый символ. Timestamp уже нормализован в UTC.
    """
    payload = asdict(submission)
    payload["timestamp"] = submission.timestamp.isoformat()
    canonical = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
