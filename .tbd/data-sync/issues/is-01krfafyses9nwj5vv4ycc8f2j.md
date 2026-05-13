---
type: is
id: is-01krfafyses9nwj5vv4ycc8f2j
title: Clarify npm before vs min-release-age and the npm/pnpm naming split
kind: task
status: open
priority: 1
version: 1
labels:
  - correctness
  - npm
dependencies: []
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:06:25.834Z
updated_at: 2026-05-13T00:06:25.834Z
---
# Clarify npm `before` vs `min-release-age` and the npm-vs-pnpm naming split

## Problem

The current operational guide (guidelines/hardening-npm.md) and research doc
mix names and units across npm and pnpm:

- npm exposes `NPM_CONFIG_BEFORE` (absolute ISO date cutoff) and, in newer
  versions, `NPM_CONFIG_MIN_RELEASE_AGE` (days). npm does not allow both at
  once.
- pnpm exposes `NPM_CONFIG_MINIMUM_RELEASE_AGE` (minutes; note the spelling
  "MINIMUM" vs npm's "MIN").
- The hardening script currently sets both `NPM_CONFIG_BEFORE` (computed
  date) and `NPM_CONFIG_MINIMUM_RELEASE_AGE=10080` (pnpm). For npm users on
  versions that support min-release-age, leaving BEFORE in place may either
  conflict or be silently ignored depending on npm version.

The doc should make the npm-vs-pnpm split obvious and prevent users from
accidentally setting `NPM_CONFIG_BEFORE` together with npm's
`NPM_CONFIG_MIN_RELEASE_AGE`.

## Fix

In research-npm-supply-chain-hardening.md and guidelines/hardening-npm.md:

- Split env-var coverage into an explicit table with columns: tool (npm vs
  pnpm), env var, unit (date vs days vs minutes), available in version, and
  notes.
- State clearly that for npm: use `NPM_CONFIG_BEFORE` for older npm or
  `NPM_CONFIG_MIN_RELEASE_AGE=7` (days) for newer; do not set both.
- State clearly that for pnpm: keep `NPM_CONFIG_MINIMUM_RELEASE_AGE=10080`
  (minutes; pnpm-specific).
- Update Step 4 ("when you intentionally need a fresh package") bypass example
  to cover both naming variants the user might have set.
- Note that npm warns and ignores unknown env config names; this is why
  pnpm-only vars are safe to set alongside npm.

## Files to edit

- guidelines/hardening-npm.md
- research/research-npm-supply-chain-hardening.md

## Acceptance

- Reader can determine within 30 seconds which env var their package manager
  honors and in what unit.
- The hardening script does not set conflicting controls.
- Bypass examples cover the full set of env vars actually in use.
