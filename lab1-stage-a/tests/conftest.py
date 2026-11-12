import pytest


@pytest.fixture
def valid_record() -> dict[str, object]:
    return {
        "submission_id": "demo-001",
        "student_id": "student-demo",
        "assignment_id": "lab-1",
        "timestamp": "2026-01-01T12:00:00+03:00",
        "text": "Учебный пример.\n",
        "code": "print('demo')\n",
        "ai_declaration": {"used": False, "details": ""},
    }
