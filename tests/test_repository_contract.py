import subprocess
import tempfile
import unittest
from collections.abc import Iterable
from pathlib import Path, PurePosixPath


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
VERSIONED_SKILL_ROOT = REPOSITORY_ROOT / "skills" / "content-radar"
VERSIONED_SKILL_REPOSITORY_PATH = PurePosixPath("skills/content-radar")
FORBIDDEN_RUNTIME_PATH_PARTS = {"state", "__pycache__"}


def versioned_skill_is_available(skill_root: Path) -> bool:
    return all(
        path.is_file()
        for path in (
            skill_root / "SKILL.md",
            skill_root / "scripts" / "fetch_aihot.py",
            skill_root / "tests" / "test_fetch_aihot.py",
        )
    )


def list_versioned_repository_paths(repository_root: Path) -> list[str]:
    resolved_root = repository_root.resolve()
    if not resolved_root.is_dir():
        raise RuntimeError(f"Repository root is not a directory: {resolved_root}")

    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(resolved_root),
                "ls-files",
                "--cached",
                "-z",
            ],
            capture_output=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as error:
        raise RuntimeError(
            f"Unable to run git ls-files in repository {resolved_root}: {error}"
        ) from error

    if result.returncode != 0:
        details = result.stderr.strip() or "<no stderr>"
        raise RuntimeError(
            "git ls-files failed in repository "
            f"{resolved_root} with exit code {result.returncode}: {details}"
        )

    return [path for path in result.stdout.split("\0") if path]


def find_forbidden_versioned_skill_paths(
    versioned_paths: Iterable[str],
) -> list[str]:
    skill_path_parts = VERSIONED_SKILL_REPOSITORY_PATH.parts
    forbidden_paths = []

    for versioned_path in versioned_paths:
        path = PurePosixPath(versioned_path)
        if path.parts[: len(skill_path_parts)] != skill_path_parts:
            continue

        relative_parts = path.parts[len(skill_path_parts) :]
        if (
            FORBIDDEN_RUNTIME_PATH_PARTS.intersection(relative_parts)
            or path.suffix == ".pyc"
        ):
            forbidden_paths.append(versioned_path)

    return sorted(forbidden_paths)


class RepositoryContractTests(unittest.TestCase):
    def setUp(self) -> None:
        if not versioned_skill_is_available(VERSIONED_SKILL_ROOT):
            self.skipTest("private_repository_only")

    def test_versioned_skill_contains_required_baseline_files(self) -> None:
        required_files = (
            VERSIONED_SKILL_ROOT / "SKILL.md",
            VERSIONED_SKILL_ROOT / "scripts" / "fetch_aihot.py",
            VERSIONED_SKILL_ROOT / "tests" / "test_fetch_aihot.py",
        )

        missing_files = [
            str(path.relative_to(REPOSITORY_ROOT))
            for path in required_files
            if not path.is_file()
        ]

        self.assertFalse(
            missing_files,
            f"Missing versioned Skill files: {missing_files}",
        )

    def test_versioned_skill_excludes_versioned_runtime_artifacts(self) -> None:
        versioned_paths = list_versioned_repository_paths(REPOSITORY_ROOT)
        forbidden_paths = find_forbidden_versioned_skill_paths(versioned_paths)

        self.assertFalse(
            forbidden_paths,
            f"Runtime artifacts must not be versioned: {forbidden_paths}",
        )


class ForbiddenVersionedSkillPathTests(unittest.TestCase):
    def test_private_contract_detects_missing_skill_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing_skill = (
                Path(temporary_directory) / "skills" / "content-radar"
            )
            self.assertFalse(versioned_skill_is_available(missing_skill))

    def test_detects_state_paths(self) -> None:
        paths = ["skills/content-radar/state/manifest.json"]

        self.assertEqual(
            find_forbidden_versioned_skill_paths(paths),
            paths,
        )

    def test_detects_pycache_paths(self) -> None:
        paths = [
            "skills/content-radar/scripts/__pycache__/runtime-cache-marker"
        ]

        self.assertEqual(
            find_forbidden_versioned_skill_paths(paths),
            paths,
        )

    def test_detects_pyc_files(self) -> None:
        paths = ["skills/content-radar/scripts/fetch_aihot.pyc"]

        self.assertEqual(
            find_forbidden_versioned_skill_paths(paths),
            paths,
        )

    def test_reports_git_command_failures_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaisesRegex(
                RuntimeError,
                r"git ls-files failed.*not a git repository",
            ):
                list_versioned_repository_paths(Path(temporary_directory))


if __name__ == "__main__":
    unittest.main()
