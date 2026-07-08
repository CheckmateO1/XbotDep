from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "main_v1.py", ROOT / "src", ROOT / "scripts"]


def iter_python_files():
    for target in TARGETS:
        if target.is_file() and target.suffix == ".py":
            yield target
        elif target.is_dir():
            for path in target.rglob("*.py"):
                if "__pycache__" not in path.parts:
                    yield path


def main():
    files = sorted(iter_python_files())
    if not files:
        raise AssertionError("No Python files found for static validation")
    for path in files:
        py_compile.compile(str(path), doraise=True)
    print(f"Python static validation passed: {len(files)} files compiled.")


if __name__ == "__main__":
    main()
