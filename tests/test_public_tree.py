from __future__ import annotations

import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.verify_public_tree import main, verify_public_tree


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_public_tree.py"


class PublicTreeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write(self, relative: str, content: str = "public\n") -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def assert_violation(
        self, relative: str, code: str, content: str = "public\n"
    ) -> None:
        self.write(relative, content)
        self.assertIn((relative, code), verify_public_tree(self.root))

    def test_accepts_exact_repository_cloud_feed_tree(self) -> None:
        self.assertEqual(
            verify_public_tree(ROOT, allow_root_git_metadata=True),
            [],
        )

    def test_root_git_metadata_exception_does_not_allow_nested_git(self) -> None:
        self.write(".git/config")
        self.write("scripts/.git/config")
        self.assertEqual(
            verify_public_tree(
                self.root,
                allow_root_git_metadata=True,
            ),
            [("scripts/.git", "forbidden_path")],
        )

    def test_accepts_synthetic_secrets_inside_tests(self) -> None:
        self.write(
            "tests/fixtures.py",
            "OPENAI='sk-proj-123456789012345678901234567890'\n"
            "GITHUB='ghp_123456789012345678901234567890'\n"
            "suggested_column='synthetic'\n",
        )
        self.assertEqual(verify_public_tree(self.root), [])

    def test_rejects_private_skill_prompt(self) -> None:
        self.write(
            "skills/content-radar/assets/chatgpt-daily-brief-prompt.md"
        )
        self.assertIn(
            ("skills", "unexpected_top_level"),
            verify_public_tree(self.root),
        )

    def test_rejects_forbidden_path_components(self) -> None:
        for relative in (
            ".env",
            "state/report.json",
            ".git/config",
            "content_radar_feed/__pycache__/module.pyc",
        ):
            with self.subTest(relative=relative):
                isolated = self.root / str(len(list(self.root.iterdir())))
                isolated.mkdir()
                path = isolated / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("private\n", encoding="utf-8")
                violations = verify_public_tree(isolated)
                rejected = next(
                    item for item in violations
                    if item[1] == "forbidden_path"
                )
                self.assertTrue(
                    relative == rejected[0]
                    or relative.startswith(rejected[0] + "/")
                )

    def test_rejects_unexpected_top_level_file(self) -> None:
        self.assert_violation("private-notes.md", "unexpected_top_level")

    def test_rejects_real_looking_credentials_without_leaking_them(self) -> None:
        secrets = (
            "sk-proj-123456789012345678901234567890",
            "ghp_123456789012345678901234567890",
            "github_pat_123456789012345678901234567890",
        )
        for index, secret in enumerate(secrets):
            with self.subTest(index=index):
                relative = f"scripts/secret-{index}.txt"
                self.write(relative, secret)
                violations = verify_public_tree(self.root)
                self.assertIn((relative, "credential"), violations)
                self.assertNotIn(secret, repr(violations))

    def test_rejects_private_editor_fields_outside_tests(self) -> None:
        for index, field in enumerate(
            ("reason", "suggested_column", "urgency_hint")
        ):
            with self.subTest(field=field):
                relative = f"scripts/editor-{index}.json"
                self.write(relative, '{"' + field + '":"private"}')
                self.assertIn(
                    (relative, "private_editor_field"),
                    verify_public_tree(self.root),
                )

    def test_rejects_symlink_outside_tree(self) -> None:
        outside = Path(self.temporary.name).parent / "outside-secret.txt"
        outside.write_text("private\n", encoding="utf-8")
        try:
            link = self.root / "scripts" / "outside"
            link.parent.mkdir(parents=True)
            link.symlink_to(outside)
            self.assertIn(
                ("scripts/outside", "symlink"),
                verify_public_tree(self.root),
            )
        finally:
            outside.unlink(missing_ok=True)

    def test_cli_emits_only_relative_path_and_code(self) -> None:
        secret = "sk-proj-123456789012345678901234567890"
        self.write("scripts/leak.txt", secret)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            result = main([str(self.root)])
        self.assertEqual(result, 1)
        self.assertEqual(stderr.getvalue(), "scripts/leak.txt:credential\n")
        self.assertNotIn(str(self.root), stderr.getvalue())
        self.assertNotIn(secret, stderr.getvalue())

    def test_script_runs_directly_against_target(self) -> None:
        self.write("requirements.txt")
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.root)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(completed.stderr, "")


if __name__ == "__main__":
    unittest.main()
