---
type: is
id: is-01krfamntd3hqvcdk8058xcj9q
title: Add doc-lint CI job that validates env-var names against an allow-list
kind: feature
status: open
priority: 3
version: 2
labels:
  - ci
  - maintenance
dependencies:
  - type: blocks
    target: is-01krfamnywbk25vg5gsv70j625
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:09:00.492Z
updated_at: 2026-05-13T00:09:13.428Z
---
# Add doc-lint CI job that validates env-var names against package-manager docs

## Problem

The UV_ONLY_BINARY bug existed because no automated check verified that
env-var names in the docs match the names the tool actually recognises.
Reviewer suggests a small CI job that lints the docs against
package-manager help output or official doc lists.

## Senior judgment

Full validation against upstream docs is fragile (their pages change
shape). A pragmatic version is:

1. An allow-list of known env-var names per ecosystem committed in the
   repo (`tests/known-env-vars.yaml` or similar).
2. A small Python or shell script that greps the docs for
   `[A-Z][A-Z0-9_]+` patterns and flags any that are not in the
   allow-list.
3. The allow-list is updated when a new env var is introduced. Stale
   allow-list entries get flagged when CI runs `grep` over the docs.

This catches the UV_ONLY_BINARY-class bug (a name that does not exist in
the allow-list ends up in the docs) without requiring a brittle live
fetch of upstream docs in CI.

## Fix

- Add tests/known-env-vars.yaml (or .txt) listing the currently-
  supported env-var names per ecosystem.
- Add a small validator script (Python stdlib) that walks
  `guidelines/`, `research/`, `SUPPLY-CHAIN-SECURITY.md`, and grep
  candidates.
- Add a CI job (.github/workflows/doc-lint.yml) running on PRs.
- Document in self-update-instructions.md: "when a new env var is
  introduced, update tests/known-env-vars.yaml at the same time."

## Files to edit / create

- New: tests/known-env-vars.yaml (or similar)
- New: tests/validate-docs.py (stdlib)
- New: .github/workflows/doc-lint.yml
- self-update-instructions.md: maintenance note

## Acceptance

- Running the script locally on the current repo passes after the
  UV_ONLY_BINARY fix.
- A PR that introduces an unknown env-var name fails CI.
- The allow-list is short enough that a human can review the diff.
