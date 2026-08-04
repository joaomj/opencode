"""Safely update the OpenCode configuration repository from origin/main."""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from subprocess import CompletedProcess
from urllib.parse import urlsplit, urlunsplit

from merge_opencode_config import (
    DEFAULT_PRESERVED_PATHS,
    merge_jsonc,
    parse_jsonc,
    write_output,
)

COMMIT_MESSAGE = "chore: update OpenCode configuration from origin/main"
CONFIG_PATH = "opencode.jsonc"


class UpdateError(RuntimeError):
    """A safe, user-facing update failure."""


def run_git_result(repository: Path, arguments: Sequence[str]) -> CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        capture_output=True,
        check=False,
        text=True,
    )


def run_git(repository: Path, arguments: Sequence[str], check: bool = True) -> str:
    result = run_git_result(repository, arguments)
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown Git error"
        raise UpdateError(f"git {' '.join(arguments)} failed: {detail}")
    return result.stdout.strip()


def redact_remote_url(remote_url: str) -> str:
    parsed = urlsplit(remote_url)
    if not parsed.password and not parsed.username:
        return remote_url
    hostname = parsed.hostname or ""
    if parsed.port:
        hostname = f"{hostname}:{parsed.port}"
    return urlunsplit((parsed.scheme, f"{parsed.username or 'user'}:***@{hostname}", parsed.path, parsed.query, parsed.fragment))


def repository_root(repository: Path) -> Path:
    root = Path(run_git(repository, ["rev-parse", "--show-toplevel"])).resolve()
    if not root.is_dir():
        raise UpdateError(f"Git root does not exist: {root}")
    return root


def assert_safe_repository(repository: Path) -> str:
    branch = run_git(repository, ["branch", "--show-current"])
    if branch != "main":
        raise UpdateError(f"current branch must be main, found: {branch or 'detached HEAD'}")

    remote_url = run_git(repository, ["remote", "get-url", "origin"])
    if not remote_url:
        raise UpdateError("origin remote is not configured")

    git_dir = Path(run_git(repository, ["rev-parse", "--git-dir"]))
    if not git_dir.is_absolute():
        git_dir = repository / git_dir
    in_progress = [
        name
        for name in ("MERGE_HEAD", "REBASE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD")
        if (git_dir / name).exists()
    ]
    if in_progress:
        raise UpdateError(f"an operation is already in progress: {', '.join(in_progress)}")

    status = run_git(repository, ["status", "--porcelain"])
    if status:
        raise UpdateError("the worktree is not clean; commit or stash local changes first")
    return remote_url


def create_backup(repository: Path, remote_url: str) -> Path:
    backup_root = repository.parent / f"{repository.name}-backups"
    backup_root.mkdir(mode=0o700, exist_ok=True)
    timestamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    backup = backup_root / timestamp
    suffix = 0
    while backup.exists():
        suffix += 1
        backup = backup_root / f"{timestamp}-{suffix}"
    backup.mkdir(mode=0o700)

    bundle = backup / "repository.bundle"
    run_git(repository, ["bundle", "create", str(bundle), "--all"])
    run_git(repository, ["bundle", "verify", str(bundle)])
    manifest = "\n".join(
        (
            f"repository={repository}",
            f"remote={redact_remote_url(remote_url)}",
            f"commit={run_git(repository, ['rev-parse', 'HEAD'])}",
            f"created={datetime.now().astimezone().isoformat()}",
            "contents=repository.bundle",
        )
    )
    (backup / "manifest.txt").write_text(f"{manifest}\n", encoding="utf-8")
    return backup


def git_object_exists(repository: Path, revision: str) -> bool:
    return run_git_result(repository, ["cat-file", "-e", revision]).returncode == 0


def read_git_file(repository: Path, revision: str) -> str:
    return run_git(repository, ["show", revision])


def abort_merge(repository: Path) -> None:
    result = run_git_result(repository, ["merge", "--abort"])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown Git error"
        raise UpdateError(f"could not abort the merge: {detail}")


def merge_candidate(repository: Path, local_config: str, upstream_config: str) -> str:
    merged = merge_jsonc(
        upstream_config,
        local_config,
        tuple(DEFAULT_PRESERVED_PATHS),
    )
    parse_jsonc(merged, "merged configuration")
    return merged


def changed_files(repository: Path) -> list[str]:
    output = run_git(repository, ["diff", "--name-status", "HEAD", "origin/main"])
    return output.splitlines() if output else []


def deleted_files(repository: Path) -> list[str]:
    output = run_git(repository, ["diff", "--diff-filter=D", "--name-only", "HEAD", "origin/main"])
    return output.splitlines() if output else []


def print_preview(repository: Path, remote_url: str, backup: Path, files: list[str]) -> None:
    print(f"Repository: {repository}")
    print(f"Origin: {redact_remote_url(remote_url)}")
    print(f"Backup: {backup}")
    print(f"Incoming files: {len(files)}")
    for file in files:
        print(f"  {file}")
    print("Preserved local configuration: " + ", ".join(DEFAULT_PRESERVED_PATHS))


def apply_update(repository: Path, merged_config: str) -> str:
    merge_result = run_git_result(repository, ["merge", "--no-commit", "--no-ff", "origin/main"])
    conflicts = run_git(repository, ["diff", "--name-only", "--diff-filter=U"])
    conflict_files = conflicts.splitlines() if conflicts else []
    if merge_result.returncode != 0 and conflict_files != [CONFIG_PATH]:
        abort_merge(repository)
        detail = merge_result.stderr.strip() or merge_result.stdout.strip() or "unknown Git error"
        raise UpdateError(f"merge conflict requires review: {', '.join(conflict_files) or detail}")
    if merge_result.returncode == 0 and conflict_files:
        abort_merge(repository)
        raise UpdateError(f"unexpected merge conflict: {', '.join(conflict_files)}")

    try:
        write_output(repository / CONFIG_PATH, merged_config)
        run_git(repository, ["add", CONFIG_PATH])
        run_git(repository, ["diff", "--check", "--cached"])
        run_git(repository, ["commit", "-m", COMMIT_MESSAGE])
    except Exception:
        merge_head = Path(run_git(repository, ["rev-parse", "--git-path", "MERGE_HEAD"]))
        if not merge_head.is_absolute():
            merge_head = repository / merge_head
        if merge_head.exists():
            abort_merge(repository)
        raise
    return run_git(repository, ["rev-parse", "HEAD"])


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="fetch and report changes without merging")
    mode.add_argument("--apply", action="store_true", help="merge and commit after safety checks")
    parser.add_argument("--repo", type=Path, help=argparse.SUPPRESS)
    options = parser.parse_args(arguments)
    if not options.apply:
        options.dry_run = True
    return options


def main(arguments: list[str] | None = None) -> int:
    try:
        options = parse_arguments(sys.argv[1:] if arguments is None else arguments)
        configured_root = Path(__file__).resolve().parents[1]
        repository = (options.repo or configured_root).resolve()
        repository = repository_root(repository)
        remote_url = assert_safe_repository(repository)
        backup = create_backup(repository, remote_url)
        run_git(repository, ["fetch", "origin", "main"])

        head = run_git(repository, ["rev-parse", "HEAD"])
        upstream = run_git(repository, ["rev-parse", "origin/main"])
        if head == upstream:
            print(f"Already up to date at {head}.")
            print(f"Backup: {backup}")
            return 0

        if not git_object_exists(repository, "HEAD:opencode.jsonc") or not git_object_exists(
            repository, "origin/main:opencode.jsonc"
        ):
            raise UpdateError("opencode.jsonc must exist in both local and upstream revisions")

        files = changed_files(repository)
        print_preview(repository, remote_url, backup, files)
        deletions = deleted_files(repository)
        if deletions:
            raise UpdateError(f"upstream deletes local files; review manually: {', '.join(deletions)}")

        local_config = read_git_file(repository, "HEAD:opencode.jsonc")
        upstream_config = read_git_file(repository, "origin/main:opencode.jsonc")
        merged_config = merge_candidate(repository, local_config, upstream_config)
        if options.dry_run:
            print("Dry run complete. No merge or commit was created.")
            return 0

        commit = apply_update(repository, merged_config)
        if run_git(repository, ["status", "--porcelain"]):
            raise UpdateError("update commit succeeded but the worktree is not clean")
        print(f"Created commit: {commit}")
        print("No remote push was performed.")
        return 0
    except (OSError, UpdateError, ValueError) as error:
        print(f"Update stopped: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
