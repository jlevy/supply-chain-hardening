---
type: is
id: is-01krfak4v29wc9b3rgzzysexzs
title: Add untrusted-repo first-run sandbox procedure for agents and humans
kind: feature
status: open
priority: 2
version: 3
labels:
  - docs
  - sandbox
  - architecture
dependencies:
  - type: blocks
    target: is-01krfamp7yt4dk01fa7wf9w24y
  - type: blocks
    target: is-01krfak4px636erwt5dz79c01d
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:08:10.338Z
updated_at: 2026-05-13T00:09:13.071Z
---
# Add untrusted-repo first-run sandbox procedure for agents and humans

## Problem

Agents in particular routinely run install/build/test commands against
freshly-cloned repos with full ambient credentials available. Reviewer is
correct that this is a major blast-radius gap: npm install scripts, Python
sdists, Rust build.rs and proc macros, Go tests, and arbitrary project
scripts all execute code at install/build time.

This is L5 of the layered model and deserves a short standalone procedure
the agent rules can reference.

## Fix

Create guidelines/untrusted-repo-first-run.md with:

1. The rule: never run install/build/test on an untrusted repo on a
   machine with ambient credentials.
2. A minimal sandbox recipe using widely available tooling:
   - Docker (preferred for cross-platform agent use): a one-liner that
     mounts the repo read-only into a fresh container with no
     credentials and restricted network egress.
   - macOS sandbox-exec or `unshare` on Linux as lighter alternatives
     (note: tooling-specific caveats).
3. The "what to remove from the sandbox" checklist:
   - No cloud creds (~/.aws, ~/.config/gcloud, etc.)
   - No SSH keys
   - No npm/PyPI/crates/GitHub publish tokens
   - No git config with email/signing keys
   - Restricted network egress (block all but, e.g., the registry the
     repo declares)
   - Clean temporary HOME
   - Read-only mount for source code where feasible
4. Per-ecosystem notes on what specifically executes:
   - npm: postinstall/preinstall scripts; mitigated by
     NPM_CONFIG_IGNORE_SCRIPTS but commodity tooling may run them
   - Python: setup.py for sdists; mitigated by UV_NO_BUILD /
     PIP_ONLY_BINARY
   - Rust: build.rs and proc-macros at any cargo build/check/test
   - Go: test files at any go test ./...; no install scripts but tests
     are code

Link from:
- README.md ("For AI Agents" intent map: "I just cloned an untrusted
  repo - what now?")
- AGENTS.md (Safety Rule block)
- Each per-ecosystem playbook (as a "before you install anything from
  this repo" pre-step)

## Acceptance

- A reader has a one-paragraph rule plus a one-screen recipe.
- The recipe is concrete enough to copy-paste for the macOS/Docker case.
- Agents can reference the doc by name in their default flow.
