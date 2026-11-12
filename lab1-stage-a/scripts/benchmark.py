"""Измерение времени приёма синтетических сдач и их повторов."""

from statistics import median
from time import perf_counter

from lab1.intake import SubmissionService
from lab1.repository import InMemorySubmissionRepository


def main() -> None:
    """Измерить медиану пяти прогонов без файлового ввода-вывода."""
    records = [
        {
            "submission_id": f"demo-{number}",
            "student_id": "student-demo",
            "assignment_id": "lab-1",
            "timestamp": "2026-01-01T09:00:00Z",
            "text": "Учебный пример.",
            "code": "print('demo')",
            "ai_declaration": {"used": False, "details": ""},
        }
        for number in range(1000)
    ]
    unique_times = []
    duplicate_times = []
    for _ in range(5):
        repository = InMemorySubmissionRepository()
        service = SubmissionService(repository)
        start = perf_counter()
        for record in records:
            service.accept(record)
        unique_times.append(perf_counter() - start)
        start = perf_counter()
        for record in records:
            service.accept(record)
        duplicate_times.append(perf_counter() - start)
        assert len(repository) == len(records)
    print(f"1000 new: {median(unique_times) * 1000:.2f} ms (median, 5 runs)")
    print(f"1000 duplicates: {median(duplicate_times) * 1000:.2f} ms (median, 5 runs)")


if __name__ == "__main__":
    main()
