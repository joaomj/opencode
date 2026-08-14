from pathlib import Path

from opencode_lint.rules.decision_notes import DecisionNotes


def test_accepts_approved_decision_note(tmp_path: Path) -> None:
    decisions_dir = tmp_path / ".agents" / "decisions"
    note = decisions_dir / "accepted" / "2026-08-14-product-choice.md"
    note.parent.mkdir(parents=True)
    note.write_text(
        """# Decision: Product choice

Status: accepted
Owner: user

## Problem
Users need a clear choice.

## Decision
Use the selected option.

## Why
It gives the best user result.

## Alternatives
The other option lost because it creates more risk.

## Product impact
Users get the intended behavior.

## Risks
The choice has a maintenance cost.

## Approval
Approved by the user.
""",
        encoding="utf-8",
    )

    violations = DecisionNotes().check_project(tmp_path)

    if violations:
        raise AssertionError(f"unexpected violations: {violations}")


def test_rejects_wrong_lifecycle_and_missing_approval(tmp_path: Path) -> None:
    decisions_dir = tmp_path / ".agents" / "decisions"
    note = decisions_dir / "proposed" / "2026-08-14-product-choice.md"
    note.parent.mkdir(parents=True)
    note.write_text(
        """# Decision: Product choice

Status: accepted
Owner: user

## Problem
Users need a clear choice.

## Decision
Use the selected option.

## Why
It gives the best user result.

## Alternatives
The other option lost.

## Product impact
Users get the intended behavior.

## Risks
The choice has a maintenance cost.

## Approval
The choice is recorded.
""",
        encoding="utf-8",
    )

    messages = [violation.message for violation in DecisionNotes().check_project(tmp_path)]

    if not any("must match lifecycle folder" in message for message in messages):
        raise AssertionError(f"missing lifecycle violation: {messages}")
    if not any("who approved" in message for message in messages):
        raise AssertionError(f"missing approval violation: {messages}")


def test_ignores_decision_readme(tmp_path: Path) -> None:
    decisions_dir = tmp_path / ".agents" / "decisions"
    decisions_dir.mkdir(parents=True)
    (decisions_dir / "README.md").write_text("# Decision Notes\n", encoding="utf-8")

    violations = DecisionNotes().check_project(tmp_path)
    if violations:
        raise AssertionError(f"unexpected violations: {violations}")
