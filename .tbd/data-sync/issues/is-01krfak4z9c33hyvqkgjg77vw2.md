---
type: is
id: is-01krfak4z9c33hyvqkgjg77vw2
title: Normalise per-playbook incident-response sections to a consistent eight-step checklist
kind: task
status: closed
priority: 3
version: 3
labels:
  - docs
  - incident-response
dependencies: []
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:08:10.472Z
updated_at: 2026-05-13T01:38:45.525Z
closed_at: 2026-05-13T01:38:45.520Z
close_reason: "Normalised all four 'If You Have Hits' sections to a consistent 8-step shape: (1) Identify scope, (2) Preserve evidence before cleanup, (3) Rotate tokens by category, (4) Check persistence mechanisms specific to payload, (5) Remove or downgrade dependency, (6) Regenerate lockfile from trusted sources, (7) Re-run scanner to confirm clean, (8) Open supply-chain-audit-log.md entry. Each playbook keeps its ecosystem-specific details inlined under the matching step (e.g., npm has SHA1HULUD runner check; Cargo has [patch.crates-io] guidance; PyPI has .pth file detection; Go has Rekoobe SSH-backdoor checks)."
---
# Make per-playbook incident-response sections consistent

## Problem

Each playbook has an "If You Have Hits" section. They are good but vary in
shape and completeness. Reviewer suggests normalising them to a consistent
checklist so a future incident reader gets the same shape regardless of
which ecosystem they hit.

## Fix

Standardize each "If You Have Hits" section to this order:

1. Identify affected machine and exact command / time window.
2. Preserve logs (shell history, npm/pip cache state, audit log dump)
   before cleanup. Important for forensics.
3. Rotate tokens by category: ecosystem publish tokens (npm, PyPI,
   crates.io, GitHub), GitHub PATs, cloud (AWS/GCP/Azure), SSH, generic
   API keys in env vars.
4. Check persistence mechanisms relevant to the payload (Shai-Hulud 2.0:
   self-hosted GitHub runner SHA1HULUD; Rekoobe: SSH backdoor on Linux;
   LiteLLM: systemd backdoor; etc.).
5. Remove or downgrade the affected dependency.
6. Regenerate lockfile from trusted sources.
7. Run scanner again to confirm clean.
8. Open a `supply-chain-audit-log.md` entry per the template.

## Files to edit

- guidelines/hardening-npm.md
- guidelines/hardening-pypi.md
- guidelines/hardening-crates.md
- guidelines/hardening-go.md
- supply-chain-audit-log-template.md: add the "evidence preservation
  before cleanup" step if missing.

## Acceptance

- All four playbooks have the same eight steps in the same order with
  per-ecosystem specifics inlined.
- The token-rotation step lists the same categories across all four with
  ecosystem-specific items pre-filled.
- Audit-log entry creation is the last step every time.
