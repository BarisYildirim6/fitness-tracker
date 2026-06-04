from __future__ import annotations

import argparse
from pathlib import Path


ROOTS = [Path("app"), Path("tests")]
EXTENSIONS = {".py"}


def iter_files() -> list[Path]:
    files: list[Path] = []
    for root in ROOTS:
        files.extend(
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix in EXTENSIONS and "__pycache__" not in path.parts
        )
    return files


def formatted_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n")
    stripped = "\n".join(line.rstrip() for line in normalized.split("\n")).rstrip()
    return f"{stripped}\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    changed: list[Path] = []
    for path in iter_files():
        current = path.read_text(encoding="utf-8")
        formatted = formatted_text(current)
        if current != formatted:
            changed.append(path)
            if not args.check:
                path.write_text(formatted, encoding="utf-8")

    if changed:
        label = "Formatting issues found" if args.check else "Formatted"
        print(f"{label}:")
        for path in changed:
            print(path)
        if args.check:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
