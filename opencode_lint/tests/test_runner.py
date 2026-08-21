from pathlib import Path

from opencode_lint.runner import LinterRunner


def test_linter_accepts_project_without_agents_file(tmp_path: Path) -> None:
    violations, exit_code = LinterRunner().run([tmp_path])

    if exit_code != 0:
        raise AssertionError(f"unexpected exit code: {exit_code}")
    if violations:
        raise AssertionError(f"unexpected violations: {violations}")


def test_local_uv_setting_satisfies_exclude_newer_policy(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.uv]\nexclude-newer = "1 week"\n',
        encoding="utf-8",
    )
    (tmp_path / "uv.lock").write_text("version = 1\n", encoding="utf-8")

    violations, exit_code = LinterRunner().run([tmp_path])

    if exit_code != 0:
        raise AssertionError(f"unexpected exit code: {exit_code}")
    if violations:
        raise AssertionError(f"unexpected violations: {violations}")


def test_directory_scan_checks_markdown_skill_descriptions(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "example" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: example\ndescription: Too short.\n---\n",
        encoding="utf-8",
    )

    violations, exit_code = LinterRunner().run([tmp_path])

    if exit_code != 0:
        raise AssertionError(f"unexpected exit code: {exit_code}")
    if not any(v.rule_id == "OC-SKILL-CHECK" for v in violations):
        raise AssertionError(f"expected skill description violation: {violations}")
