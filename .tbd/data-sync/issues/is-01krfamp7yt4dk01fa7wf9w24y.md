---
type: is
id: is-01krfamp7yt4dk01fa7wf9w24y
title: Strengthen AGENTS.md / SUPPLY-CHAIN-SECURITY.md agent rules and audit-log redaction
kind: task
status: open
priority: 2
version: 1
labels:
  - docs
  - agents
dependencies: []
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:09:00.925Z
updated_at: 2026-05-13T00:09:00.925Z
---
# Strengthen AGENTS.md / SUPPLY-CHAIN-SECURITY.md agent rules

## Problem

Several rule additions are worth promoting to the agent-facing docs that
agents pick up automatically (AGENTS.md and the portable
SUPPLY-CHAIN-SECURITY.md). These are short but high-leverage.

## Fix

Add to AGENTS.md "Safety Rule For Agents" block (or wherever rules live):

- "Do not run install/build/test in an untrusted repo on a machine with
  ambient credentials. Use the sandbox procedure in
  guidelines/untrusted-repo-first-run.md." (Depends on the
  untrusted-repo bead.)
- "Avoid `npx`, `pnpm dlx`, `bunx`, `uvx`, and `go run <remote>`
  without pinning and explicit review."
- "Do not run `curl | sh` install commands from untrusted sources.
  Verify the installer URL belongs to the documented project; verify
  signatures or checksums where available."
- "Treat fresh repos as untrusted by default. Run no install/build/test
  until either the cool-off window has passed or the package is
  explicitly approved."

Mirror the relevant additions in SUPPLY-CHAIN-SECURITY.md.

In supply-chain-audit-log-template.md add a redaction note: "Never
paste live tokens, secrets, private keys, or sensitive internal paths
into the audit log unless it is private and access-controlled."

## Files to edit

- AGENTS.md
- SUPPLY-CHAIN-SECURITY.md
- supply-chain-audit-log-template.md

## Acceptance

- Agents picking up AGENTS.md see the new rules in the safety block.
- SUPPLY-CHAIN-SECURITY.md gains a "Do not curl | sh from untrusted"
  rule.
- Audit-log template warns about credential leakage.
