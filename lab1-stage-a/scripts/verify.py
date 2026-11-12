"""Локальный quality gate с безопасным отчётом для коммита."""

import json
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """Выполнить проверки и записать только агрегированные результаты.

    Сырые отчёты содержат пути и остаются в игнорируемом каталоге.
    Код завершения ненулевой, если хотя бы одна проверка не прошла.
    """
    artifacts = ROOT / ".artifacts"
    artifacts.mkdir(exist_ok=True)
    coverage_path = artifacts / "coverage.json"
    coverage_path.unlink(missing_ok=True)
    junit_path = artifacts / "pytest.xml"
    junit_path.unlink(missing_ok=True)
    checks = [
        ("Ruff lint", ["ruff", "check", "."]),
        ("Ruff format", ["ruff", "format", "--check", "."]),
        ("mypy", ["mypy", "src/"]),
        (
            "pytest + coverage",
            [
                "pytest",
                "-q",
                "--cov=lab1",
                "--cov-branch",
                "--cov-report=term-missing",
                "--cov-report=json:.artifacts/coverage.json",
                "--junitxml=.artifacts/pytest.xml",
            ],
        ),
    ]
    python_version = ".".join(str(part) for part in sys.version_info[:3])
    report = [
        "# Проверки этапа А",
        "",
        f"Python: {python_version}",
        "",
        "| Проверка | Результат |",
        "|---|---|",
    ]
    success = True
    for name, args in checks:
        result = subprocess.run([sys.executable, "-m", *args], cwd=ROOT, check=False)
        passed = result.returncode == 0
        success = success and passed
        report.append(f"| {name} | {'PASS' if passed else 'FAIL'} |")
    if junit_path.exists():
        suites = ElementTree.parse(junit_path).getroot().findall("testsuite")
        counts = {
            key: sum(int(suite.get(key, "0")) for suite in suites)
            for key in ("tests", "failures", "errors", "skipped")
        }
        report.extend(
            [
                "",
                f"Тесты: {counts['tests']}; ошибок: {counts['errors']}; "
                f"провалов: {counts['failures']}; пропущено: {counts['skipped']}.",
            ]
        )
    if coverage_path.exists():
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        percent = coverage["totals"]["percent_covered"]
        report.extend(["", f"Покрытие с ветвлениями: {percent:.2f}%."])
    report.extend(["", "Версии инструментов:", ""])
    for name in ("pytest", "pytest-cov", "ruff", "mypy"):
        try:
            installed = version(name)
        except PackageNotFoundError:
            installed = "не установлен"
        report.append(f"- {name}: {installed}")
    report.extend(
        [
            "",
            f"Итог: {'PASS' if success else 'FAIL'}.",
            "",
            "Отчёт не включает абсолютные пути, переменные окружения и данные сдач.",
        ]
    )
    (ROOT / "docs" / "verification-local.md").write_text(
        "\n".join(report) + "\n", encoding="utf-8"
    )
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
