---
type: is
id: is-01krfaemv32r3m2wdtbkz2k4ht
title: Correct pip config precedence in PyPI research doc
kind: bug
status: closed
priority: 0
version: 3
labels:
  - correctness
  - pypi
dependencies: []
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:05:42.882Z
updated_at: 2026-05-13T01:22:46.265Z
closed_at: 2026-05-13T01:22:46.260Z
close_reason: "Rewrote pip precedence chain to reflect actual pip behavior: CLI > PIP_* env > PIP_CONFIG_FILE > site > user > global INI configs. Removed false claim that pip reads pyproject.toml [tool.pip] / setup.cfg. Updated 'Operational conclusion' to distinguish pip (project-local files are not a pip config source) from uv (project config is a real layer)."
---
# Correct pip config precedence in PyPI research doc

## Problem

research/research-pypi-supply-chain-hardening.md (section "pip Precedence")
documents this chain:

```
HIGHEST PRIORITY  ->  command-line flag
                  ->  environment variable (PIP_* prefix)
                  ->  project-local config (pyproject.toml [tool.pip], setup.cfg)
                  ->  user config
                  ->  global config
LOWEST PRIORITY   ->  pip builtin defaults
```

The "project-local config (pyproject.toml [tool.pip], setup.cfg)" entry is
incorrect. Verified against pip.pypa.io/en/stable/topics/configuration/ as of
2026-05-12: pip reads global/user/site INI configs, plus PIP_CONFIG_FILE if
set, plus PIP_* env vars, plus CLI flags. pip does not honor
`[tool.pip]` in pyproject.toml as a config source for install hardening. The
site config is the per-virtualenv pip.conf, not a project file.

This matters because the document's own conclusion section says "Project-local
configuration (pyproject.toml, setup.cfg) can override user-level settings.
Environment variables are the only setting that beats project-local config in
the precedence chain for both pip and uv." That conclusion is wrong for pip.

## Fix

Rewrite the pip precedence chain to:

```
HIGHEST PRIORITY  ->  command-line flag (--uploaded-prior-to, --only-binary, etc.)
                  ->  environment variable (PIP_* prefix)
                  ->  PIP_CONFIG_FILE (if set)
                  ->  site config ($VIRTUAL_ENV/pip.conf)
                  ->  user config (~/.config/pip/pip.conf, etc.)
                  ->  global config (/etc/pip.conf, etc.)
LOWEST PRIORITY   ->  pip builtin defaults
```

Add a separate note: project metadata (pyproject.toml, setup.cfg, PEP 517
build backends) can influence dependency resolution, extras, and source-build
behavior, but pip does not read it as a config layer the way uv reads
[tool.uv].

Update the "Operational conclusion" paragraph to reflect that env vars beat
all pip config files but not CLI flags. Remove the "project-local config can
override user-level" claim for pip; keep it for uv where it is correct.

## Files to edit

- research/research-pypi-supply-chain-hardening.md
- Anywhere else this claim is repeated (grep for "tool.pip" and "setup.cfg" in
  the repo).

## Acceptance

- pip precedence chain matches pip's documented behavior.
- uv precedence chain is unchanged (it is correct as written).
- The "Operational conclusion" no longer implies pip honors project-local
  config files.
