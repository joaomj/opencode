import shutil
import subprocess
from pathlib import Path

from opencode_lint.runner import LinterRunner


def _run_git(directory: Path, *arguments: str) -> None:
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("Git is required for this test")
    subprocess.run([git, *arguments], cwd=directory, check=True)  # noqa: S603


def test_linter_accepts_project_without_agents_file(tmp_path: Path) -> None:
    violations, exit_code = LinterRunner().run([tmp_path])

    if exit_code != 0:
        raise AssertionError(f"unexpected exit code: {exit_code}")
    if violations:
        raise AssertionError(f"unexpected violations: {violations}")


def test_explicit_markdown_target_checks_skill_descriptions(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "example" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: example\ndescription: Too short.\n---\n",
        encoding="utf-8",
    )

    violations, exit_code = LinterRunner().run([skill])

    if exit_code != 0:
        raise AssertionError(f"unexpected exit code: {exit_code}")
    if not any(v.rule_id == "OC-SKILL-CHECK" for v in violations):
        raise AssertionError(f"expected skill description violation: {violations}")


def test_directory_scan_ignores_markdown_by_default(tmp_path: Path) -> None:
    document = tmp_path / "README.md"
    document.write_text("# Title \u2014 details\n", encoding="utf-8")

    violations, exit_code = LinterRunner().run([tmp_path])

    if exit_code != 0:
        raise AssertionError(f"unexpected exit code: {exit_code}")
    if any(v.file_path == document for v in violations):
        raise AssertionError(f"documentation should not be linted by directory scan: {violations}")


def test_syntax_errors_fail_closed(tmp_path: Path) -> None:
    source = tmp_path / "broken.py"
    source.write_text("def broken(:\n    pass\n", encoding="utf-8")

    violations, exit_code = LinterRunner(profile="fast").run([source])

    if exit_code != 1:
        raise AssertionError(f"expected a blocking exit code: {exit_code}")
    if not any(v.rule_id == "LNT022" for v in violations):
        raise AssertionError(f"expected fail-closed violation: {violations}")
    failure = next(v for v in violations if v.rule_id == "LNT022")
    if "invalid syntax" not in failure.message:
        raise AssertionError(f"expected a specific syntax error reason: {failure.message}")


def test_broad_suppression_is_blocked(tmp_path: Path) -> None:
    source = tmp_path / "source.py"
    source.write_text("value = 1  # noqa\n", encoding="utf-8")

    violations, exit_code = LinterRunner(profile="fast").run([source])

    if exit_code != 1:
        raise AssertionError(f"expected a blocking exit code: {exit_code}")
    if not any(v.rule_id == "LNT004" for v in violations):
        raise AssertionError(f"expected suppression violation: {violations}")


def test_quality_lint_on_non_code_content_is_a_warning(tmp_path: Path) -> None:
    document = tmp_path / "README.md"
    document.write_text("value = 1  # noqa\n", encoding="utf-8")

    violations, exit_code = LinterRunner(profile="fast").run([document])

    if exit_code != 0:
        raise AssertionError(f"expected non-code lint to remain non-blocking: {exit_code}")
    suppression = next(v for v in violations if v.rule_id == "LNT004")
    if suppression.severity != "warning":
        raise AssertionError(f"expected a warning for non-code content: {suppression}")


def test_security_lint_on_non_code_content_remains_an_error(tmp_path: Path) -> None:
    compose = tmp_path / "docker-compose.yml"
    compose.write_text(
        "services:\n  app:\n    image: example\n    privileged: true\n",
        encoding="utf-8",
    )

    violations, exit_code = LinterRunner(profile="fast").run([compose])

    if exit_code != 1:
        raise AssertionError(f"expected security lint to remain blocking: {exit_code}")
    privileged = next(v for v in violations if v.rule_id == "OC003")
    if privileged.severity != "error":
        raise AssertionError(f"expected an error for privileged containers: {privileged}")


def test_invalid_compose_yaml_fails_closed(tmp_path: Path) -> None:
    compose = tmp_path / "docker-compose.yml"
    compose.write_text("services:\n  app: [\n", encoding="utf-8")

    violations, exit_code = LinterRunner(profile="fast").run([compose])

    if exit_code != 1:
        raise AssertionError(f"expected a blocking exit code: {exit_code}")
    if not any(v.rule_id == "LNT022" for v in violations):
        raise AssertionError(f"expected YAML fail-closed violation: {violations}")
    failure = next(v for v in violations if v.rule_id == "LNT022")
    if "expected" not in failure.message.lower():
        raise AssertionError(f"expected a specific YAML error reason: {failure.message}")


def test_staged_plan_file_is_blocked(tmp_path: Path) -> None:
    _run_git(tmp_path, "init", "-q")
    plan = tmp_path / "release-plan.md"
    plan.write_text("# Local plan\n", encoding="utf-8")
    _run_git(tmp_path, "add", "release-plan.md")

    violations, exit_code = LinterRunner(profile="fast").run([plan])

    if exit_code != 1:
        raise AssertionError(f"expected a blocking exit code: {exit_code}")
    if not any(v.rule_id == "LNT025" for v in violations):
        raise AssertionError(f"expected staged artifact violation: {violations}")


def test_changed_python_argument_budget_is_blocking(tmp_path: Path) -> None:
    _run_git(tmp_path, "init", "-q")
    source = tmp_path / "source.py"
    source.write_text(
        "def too_many(one, two, three, four, five, six, seven):\n    return one\n",
        encoding="utf-8",
    )
    _run_git(tmp_path, "add", "source.py")

    violations, exit_code = LinterRunner(profile="fast").run([source])

    if exit_code != 1:
        raise AssertionError(f"expected a blocking exit code: {exit_code}")
    if not any(v.rule_id == "LNT-PY-BUDGET" for v in violations):
        raise AssertionError(f"expected Python budget violation: {violations}")
