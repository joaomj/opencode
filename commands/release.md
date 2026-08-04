---
description: Create a user-approved GitHub release with generated release notes and changelog
---

Create a GitHub release for `$ARGUMENTS` and update the CHANGELOG.md file.

1. Require an explicit version argument such as `v4.0.0`. Ask for it if it is
   missing. Do not infer a version from the current tags.
2. Inspect the worktree, current branch, remote, existing tags, and releases.
   Stop if the worktree has uncommitted changes or the version already exists.
3. Identify the previous release and commits included in the new version.
4. Generate concise release notes grouped by user-visible area. Include
   improvements, bug fixes, and community contributors only when applicable.
   Do not use GitHub's automatic notes as a substitute for reviewing the
   generated notes.
5. Prepare the changelog entry for this version from the same commits,
   following Keep a Changelog conventions
   (https://keepachangelog.com/en/1.1.0/):
   - sections Added, Fixed, and Changed; breaking changes (`!` in the commit
     subject or `BREAKING CHANGE` in the body) go in Changed prefixed with
     "Breaking: "
   - one concise bullet per user-visible change, excluding `docs`, `chore`,
     `style`, `test`, `build`, and `ci` commits unless the change is
     user-visible
   - link pull requests when present in the commit subject:
     `[PR #123](https://github.com/<owner>/<repo>/pull/123)`
   - heading `## [<version>] - <YYYY-MM-DD>` without the leading `v`, inserted
     below the `## [Unreleased]` heading, newest first; move existing
     Unreleased entries into the new section, dropping duplicates
   - update the compare links: Unreleased compares the new version to HEAD,
     the new version compares the previous version to the new version; use
     the tag URL when there is no previous version
6. Show the proposed version, target commit, tag, complete release notes, and
   the complete changelog entry. Ask the user to approve the exact release
   contents before any remote write or changelog edit.
7. After approval, update the CHANGELOG.md file, commit that change, push the
   target branch, create the version tag on the changelog commit, and publish
   the GitHub release with the approved notes using `gh`. If the changelog
   file is unchanged, tag the originally approved commit.
8. Verify that the remote branch and tag point to the changelog commit and
   that the release is published with the approved notes.
9. Report the release URL, tag, commit, changelog commit, and any failed or
   skipped verification.

Do not create a release, tag, commit, or pull request before the user approves
the proposed release contents. Do not modify the changelog file before the
user approves the complete proposed release contents.
