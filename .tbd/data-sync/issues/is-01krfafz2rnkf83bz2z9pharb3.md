---
type: is
id: is-01krfafz2rnkf83bz2z9pharb3
title: Tighten cool-off-across-all-package-managers framing in README and portable doc
kind: task
status: open
priority: 1
version: 1
labels:
  - correctness
  - docs
dependencies: []
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:06:26.135Z
updated_at: 2026-05-13T00:06:26.135Z
---
# Tighten the "cool-off across all main package managers" framing

## Problem

README.md, SUPPLY-CHAIN-SECURITY.md, and per-ecosystem summaries use language
that suggests a uniform "cool-off period" / "7-day release-age delay" applies
across npm, PyPI, crates.io, and Go. That is accurate for:

- npm (NPM_CONFIG_BEFORE, NPM_CONFIG_MIN_RELEASE_AGE)
- pnpm (NPM_CONFIG_MINIMUM_RELEASE_AGE)
- uv (UV_EXCLUDE_NEWER)
- pip 26.1+ (PIP_UPLOADED_PRIOR_TO)
- poetry 2.4.0+ (solver.min-release-age)
- pdm (--exclude-newer)

It is **not** accurate for Cargo or Go modules as written. Those ecosystems
get their supply-chain protection from lockfile enforcement, checksum
verification, source restrictions, vetting, and scanning. Release-age gating
on those ecosystems requires Renovate/Dependabot, internal mirrors, or
update wrappers, none of which are core in our playbooks.

Reviewer is correct to flag this. Overgeneralizing the "cool-off" pattern
makes Cargo and Go readers think they have a control they do not.

## Fix

In README.md ("Why The Hardening Pattern Is Stable" section) and
SUPPLY-CHAIN-SECURITY.md (Install Rules + Why section):

- Rewrite the core pattern statement to:
  "Delay newly-published versions where the package manager supports it.
  Otherwise, prevent unintentional re-resolution, pin exact versions, verify
  checksums/advisories, and require explicit human review for dependency
  updates."
- For SUPPLY-CHAIN-SECURITY.md Rule 1 ("Never install a version newer than 7
  days old"): explicitly note that for Cargo and Go the rule is enforced
  through `--locked` / committed lockfiles + explicit human review for
  version bumps, not a native release-age flag. Or scope Rule 1 to the
  ecosystems that natively support it and add a separate rule for Cargo/Go.

In guidelines/hardening-crates.md and guidelines/hardening-go.md: confirm
the docs do not imply release-age gating is native; current versions look
ok but verify.

## Files to edit

- README.md
- SUPPLY-CHAIN-SECURITY.md
- guidelines/hardening-crates.md (verify wording only)
- guidelines/hardening-go.md (verify wording only)

## Acceptance

- A Cargo or Go reader can not mistake the framing for "you also have a
  release-age cool-off knob."
- The "core pattern" claim is preserved for npm and PyPI where it is
  correct.
- "Defeats nearly all of it" / "defeats nearly every named incident"
  hyperbole is bounded; see related bead on language tightening.
