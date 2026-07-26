#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import re
import sys
from typing import Iterable, List, Sequence, Tuple


ALLOWED_TOP_LEVEL = {
    ".github",
    ".gitignore",
    "content_radar_feed",
    "requirements.txt",
    "schema",
    "scripts",
    "tests",
}
FORBIDDEN_COMPONENTS = {".env", "state", ".git", "__pycache__"}
PRIVATE_FIELD_GUARD_FILES = {
    "content_radar_feed/privacy.py",
}
CREDENTIAL_PATTERNS = (
    re.compile(r"(?<![A-Za-z0-9_])sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?<![A-Za-z0-9_])gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"(?<![A-Za-z0-9_])github_pat_[A-Za-z0-9_]{20,}"),
)
PRIVATE_FIELDS = (
    "rea" + "son",
    "suggested" + "_column",
    "urgency" + "_hint",
)
PRIVATE_FIELD_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_])(?:"
    + "|".join(re.escape(value) for value in PRIVATE_FIELDS)
    + r")(?![A-Za-z0-9_])"
)

Violation = Tuple[str, str]


def _relative(path: Path, root: Path) -> str:
    value = path.relative_to(root).as_posix()
    return value or "."


def _path_code(relative: str) -> str:
    parts = Path(relative).parts
    if any(part in FORBIDDEN_COMPONENTS for part in parts):
        return "forbidden_path"
    if parts and parts[0] not in ALLOWED_TOP_LEVEL:
        return "unexpected_top_level"
    return ""


def _scan_file(path: Path, relative: str) -> Iterable[Violation]:
    if relative == "tests" or relative.startswith("tests/"):
        return ()
    try:
        text = path.read_bytes().decode("utf-8", errors="replace")
    except OSError:
        return ((relative, "unreadable_file"),)
    violations: List[Violation] = []
    if any(pattern.search(text) for pattern in CREDENTIAL_PATTERNS):
        violations.append((relative, "credential"))
    if (
        relative not in PRIVATE_FIELD_GUARD_FILES
        and PRIVATE_FIELD_PATTERN.search(text)
    ):
        violations.append((relative, "private_editor_field"))
    return violations


def verify_public_tree(
    root: Path,
    *,
    allow_root_git_metadata: bool = False,
) -> List[Violation]:
    root = Path(root)
    if root.is_symlink():
        return [(".", "symlink")]
    if not root.is_dir():
        return [(".", "root_invalid")]

    violations: List[Violation] = []
    for current, directory_names, file_names in os.walk(
        root, topdown=True, followlinks=False
    ):
        current_path = Path(current)
        kept_directories = []
        for name in sorted(directory_names):
            path = current_path / name
            relative = _relative(path, root)
            if (
                allow_root_git_metadata
                and current_path == root
                and name == ".git"
            ):
                continue
            if path.is_symlink():
                violations.append((relative, "symlink"))
                continue
            code = _path_code(relative)
            if code:
                violations.append((relative, code))
                continue
            kept_directories.append(name)
        directory_names[:] = kept_directories

        for name in sorted(file_names):
            path = current_path / name
            relative = _relative(path, root)
            if path.is_symlink():
                violations.append((relative, "symlink"))
                continue
            code = _path_code(relative)
            if code:
                violations.append((relative, code))
                continue
            violations.extend(_scan_file(path, relative))

    return sorted(set(violations))


def main(argv: Sequence[str] = ()) -> int:
    arguments = list(argv)
    if len(arguments) > 1:
        print(".:usage", file=sys.stderr)
        return 2
    root = Path(arguments[0]) if arguments else Path(".")
    violations = verify_public_tree(root)
    for relative, code in violations:
        print(f"{relative}:{code}", file=sys.stderr)
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
