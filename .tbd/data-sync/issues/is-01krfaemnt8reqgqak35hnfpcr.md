---
type: is
id: is-01krfaemnt8reqgqak35hnfpcr
title: Replace UV_ONLY_BINARY with UV_NO_BUILD and only-binary project config
kind: bug
status: open
priority: 0
version: 2
labels:
  - correctness
  - pypi
dependencies:
  - type: blocks
    target: is-01krfamntd3hqvcdk8058xcj9q
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:05:42.713Z
updated_at: 2026-05-13T00:09:13.313Z
---
# Replace UV_ONLY_BINARY with correct uv controls

## Problem

`UV_ONLY_BINARY` is used as an env var in:

- guidelines/hardening-pypi.md (Step 1 hardening script, Step 3 verify, Step 4
  bypass, CI YAML)
- research/research-pypi-supply-chain-hardening.md (multiple places: hardening
  script, env-var conclusion section, CI examples, opt-out example, operational
  checklist)
- README references (indirect)

It is **not a documented uv environment variable** (verified against
docs.astral.sh/uv/reference/environment/ as of 2026-05-12). uv exposes
`UV_NO_BUILD` (equivalent to `--no-build`, refuses sdist builds) and
`UV_NO_BINARY` (equivalent to `--no-binary`, forces source builds). The
`--only-binary :all:` flag is a CLI option and a project config option under
`[tool.uv.pip]`, but not an env var.

This is dangerous because users who set `UV_ONLY_BINARY=":all:"` believe uv is
refusing sdists when uv silently ignores the variable.

## Fix

Replace every occurrence:

- Hardening script: drop `UV_ONLY_BINARY=":all:"`, add `UV_NO_BUILD=true`.
- Verify step: `echo "$UV_NO_BUILD"` should show `true`.
- Bypass example: `UV_EXCLUDE_NEWER= UV_NO_BUILD= uv pip install some-pkg`.
- CI examples: replace `UV_ONLY_BINARY: ":all:"` with `UV_NO_BUILD: "true"`.
- For project-mode uv, document `no-build = true` under `[tool.uv]` in
  pyproject.toml (already mentioned in research doc; keep and emphasize).
- For pip-style uv flows (uv pip), document `only-binary = [":all:"]` under
  `[tool.uv.pip]` in pyproject.toml/uv.toml as an optional project-level config.

## Files to edit

- guidelines/hardening-pypi.md
- research/research-pypi-supply-chain-hardening.md
- Any references in README.md, AGENTS.md, SUPPLY-CHAIN-SECURITY.md (likely none
  but grep to confirm)

## Acceptance

- `grep -r UV_ONLY_BINARY .` returns no hits in committed docs.
- Verify command in hardening-pypi.md actually demonstrates the env var is
  active (do not just echo the variable; see related verification bead).
- A note explains the difference between UV_NO_BUILD (env var, refuses sdists)
  and only-binary project config (project-level alternative).
