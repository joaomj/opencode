---
description: Create a user-approved GitHub release with generated release notes
---

Create a GitHub release for `$ARGUMENTS`.

1. Require an explicit version argument such as `v4.0.0`. Ask for it if it is
   missing. Do not infer a version from the current tags.
2. Inspect the worktree, current branch, remote, existing tags, and releases.
   Stop if the worktree has uncommitted changes or the version already exists.
3. Identify the previous release and commits included in the new version.
4. Generate concise release notes grouped by user-visible area. Include
   improvements, bug fixes, and community contributors only when applicable.
   Do not use GitHub's automatic notes as a substitute for reviewing the
   generated notes.
5. Show the proposed version, target commit, tag, and complete release notes.
   Ask the user to approve the exact release contents before any remote write.
6. After approval, push the target branch, create the version tag, and publish
   the GitHub release with the approved notes using `gh`.
7. Verify that the remote branch and tag point to the target commit and that
   the release is published with the approved notes.
8. Report the release URL, tag, commit, and any failed or skipped verification.

Do not create a release, tag, commit, or pull request before the user approves
the proposed release contents. Do not modify a persistent changelog file unless
the user explicitly requests it.
