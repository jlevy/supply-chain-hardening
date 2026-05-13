---
type: is
id: is-01krfaht36k450vtkxyd6jgtbq
title: Add Strict / Balanced / Emergency-Exception mode matrix and exception template
kind: feature
status: open
priority: 2
version: 3
labels:
  - docs
  - strict-mode
dependencies:
  - type: blocks
    target: is-01krfamp7yt4dk01fa7wf9w24y
  - type: blocks
    target: is-01krfak4px636erwt5dz79c01d
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:07:26.565Z
updated_at: 2026-05-13T00:09:13.185Z
---
# Add Strict / Balanced / Emergency-Exception mode matrix and exception template

## Problem

The current playbooks present one configuration that applies to all users.
Real teams have different risk tolerances and different exception flows.
Reviewer is correct that a tiered model makes the docs more usable.

## Fix

Add a new section (likely at the top of each per-ecosystem playbook or as
a shared appendix linked from each) that documents three modes:

- **Balanced (default)**: 7-day cool-off, no install scripts, frozen
  lockfiles. The current recommendation.
- **Strict**: balanced plus no `npx`/`pnpm dlx`/`bunx`/`uvx`/`go run remote`,
  GOTOOLCHAIN=local, sandbox for untrusted repos, hash-pinned requirements
  for pip, signed-attestations check where PyPI Trusted Publishers is used.
- **Emergency CVE exception**: a documented procedure for the case where a
  fresh patch must be installed inside the cool-off window. Requires
  per-command bypass with reason logged.

Add a "safe install exception record" template (small, copyable into the
audit log or PR body):

```
Package: <name>
Version: <pinned exact version>
Reason: <why this exception is necessary>
Source verification: <what was checked: signing, sigstore, OSV scan, etc.>
Approver: <human>
Rollback plan: <how to undo if it turns bad>
```

## Files to edit

- New: guidelines/strict-mode.md (or guidelines/security-modes.md)
- README.md: link to the new file
- AGENTS.md: link to the new file (agents should default to balanced;
  strict for high-risk environments)
- supply-chain-audit-log-template.md: add exception-record subsection

## Acceptance

- A reader can pick balanced or strict in under a minute.
- The exception template is short enough to fill in for a single install.
- Agents have a clear rule: balanced by default, strict if the repo
  declares it.
