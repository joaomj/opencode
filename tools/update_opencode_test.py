"""End-to-end tests for the OpenCode update command."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from merge_opencode_config import parse_jsonc

SCRIPT = Path(__file__).with_name("update_opencode.py")


def run_git(repository: Path, arguments: list[str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
    return result.stdout.strip()


class UpdateOpenCodeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.remote = self.root / "remote.git"
        self.local = self.root / "local"
        self.upstream = self.root / "upstream"

        run_git(self.root, ["init", "--bare", str(self.remote)])
        self.clone(self.local)
        self.configure_identity(self.local)
        self.write(self.local / "opencode.jsonc", '{\n  "snapshot": false\n}\n')
        self.write(self.local / "commands" / "base.md", "base\n")
        run_git(self.local, ["add", "."])
        run_git(self.local, ["commit", "-m", "initial"])
        run_git(self.local, ["branch", "-M", "main"])
        run_git(self.local, ["push", "-u", "origin", "main"])

        self.clone(self.upstream, branch="main")
        self.configure_identity(self.upstream)
        self.write(
            self.local / "opencode.jsonc",
            """{
  \"provider\": { \"local\": { \"models\": { \"custom\": {} } } },
  \"permission\": { \"bash\": \"deny\" },
  \"small_model\": \"local/small\",
  \"local_only\": true,
  \"snapshot\": false
}
""",
        )
        run_git(self.local, ["add", "."])
        run_git(self.local, ["commit", "-m", "customize local settings"])

        self.write(
            self.upstream / "opencode.jsonc",
            """{
  \"provider\": { \"upstream\": { \"models\": { \"default\": {} } } },
  \"permission\": { \"bash\": \"allow\" },
  \"small_model\": \"upstream/small\",
  \"autoupdate\": \"notify\",
  \"snapshot\": true
}
""",
        )
        self.write(self.upstream / "commands" / "upstream.md", "upstream\n")
        run_git(self.upstream, ["add", "."])
        run_git(self.upstream, ["commit", "-m", "upstream update"])
        run_git(self.upstream, ["push", "origin", "main"])

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_preview_then_apply_preserves_local_settings(self) -> None:
        preview = self.run_update("--preview")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertIn("Preview complete", preview.stdout)
        self.assertFalse((self.local / "commands" / "upstream.md").exists())
        self.assertTrue((self.local.parent / "local-backups").is_dir())

        applied = self.run_update("--apply")
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertIn("Created commit", applied.stdout)

        config = parse_jsonc((self.local / "opencode.jsonc").read_text(), "test configuration").value
        self.assertIsInstance(config, dict)
        self.assertIn("local", config["provider"])
        self.assertNotIn("upstream", config["provider"])
        self.assertEqual(config["permission"]["bash"], "deny")
        self.assertEqual(config["small_model"], "local/small")
        self.assertTrue(config["local_only"])
        self.assertEqual(config["autoupdate"], "notify")
        self.assertTrue((self.local / "commands" / "upstream.md").exists())
        self.assertEqual(run_git(self.local, ["status", "--porcelain"]), "")

    def test_stops_before_backup_when_worktree_is_dirty(self) -> None:
        self.write(self.local / "uncommitted.md", "do not overwrite\n")
        result = self.run_update("--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("worktree is not clean", result.stderr)
        self.assertFalse((self.local.parent / "local-backups").exists())
        self.assertEqual((self.local / "uncommitted.md").read_text(), "do not overwrite\n")

    def clone(self, destination: Path, branch: str | None = None) -> None:
        arguments = ["clone"]
        if branch:
            arguments.extend(["--branch", branch])
        arguments.extend([str(self.remote), str(destination)])
        run_git(self.root, arguments)

    def configure_identity(self, repository: Path) -> None:
        run_git(repository, ["config", "user.email", "test@example.invalid"])
        run_git(repository, ["config", "user.name", "OpenCode Test"])

    def write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def run_update(self, mode: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(self.local), mode],
            capture_output=True,
            check=False,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
