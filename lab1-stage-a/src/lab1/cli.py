"""Командная строка для импорта без бизнес-логики в интерфейсе."""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from lab1.importer import import_file
from lab1.intake import SubmissionService
from lab1.repository import InMemorySubmissionRepository


def main(argv: list[str] | None = None) -> int:
    """Выполнить CLI и вернуть код завершения.

    Returns:
        0 — все строки приняты или уже существуют; 1 — есть ошибки строк;
        2 — неверный вызов CLI или недоступный файл.
    """
    parser = argparse.ArgumentParser(prog="lab1")
    commands = parser.add_subparsers(dest="command", required=True)
    import_command = commands.add_parser("import", help="Импорт сдач из JSONL")
    import_command.add_argument("path", type=Path, help="Файл JSONL в UTF-8")
    args = parser.parse_args(argv)

    service = SubmissionService(InMemorySubmissionRepository())
    try:
        report = import_file(args.path, service)
    except OSError:
        print("Не удалось открыть или прочитать файл импорта.", file=sys.stderr)
        return 2
    print(json.dumps(asdict(report), ensure_ascii=True, indent=2))
    return 1 if report.errors else 0
