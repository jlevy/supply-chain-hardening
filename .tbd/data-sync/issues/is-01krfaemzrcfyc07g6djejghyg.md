---
type: is
id: is-01krfaemzrcfyc07g6djejghyg
title: Fix pnpm config-source semantics in npm research doc
kind: bug
status: open
priority: 0
version: 1
labels:
  - correctness
  - npm
dependencies: []
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:05:43.032Z
updated_at: 2026-05-13T00:05:43.032Z
---
# Fix pnpm config-source semantics in npm research doc

## Problem

research/research-npm-supply-chain-hardening.md (and possibly
guidelines/hardening-npm.md by reference) describes pnpm and npm config as
sharing the same layered .npmrc precedence. That is no longer accurate for
current pnpm.

Verified against pnpm.io/settings as of 2026-05-12: pnpm reads CLI args, env
vars, pnpm-workspace.yaml (per-project), and ~/.config/pnpm/config.yaml
(global). .npmrc is read only for auth and registry settings. Non-auth pnpm
settings like hoistPattern, nodeLinker, shamefullyHoist, and importantly the
build-script allowlist must be configured in pnpm-workspace.yaml or the global
config.yaml.

## Fix

In research-npm-supply-chain-hardening.md:

- Update the precedence / config-source explanation to distinguish npm
  (layered .npmrc) from pnpm (CLI > env > pnpm-workspace.yaml > global
  config.yaml; .npmrc auth/registry only).
- Note that environment variables remain the cross-tool way to enforce
  process-level defaults.
- Note that project-level pnpm policy belongs in pnpm-workspace.yaml, not
  .npmrc.

In guidelines/hardening-npm.md: confirm the operational guide does not assert
.npmrc behavior incorrectly. Current guide is env-var-first which is fine,
but if any "Where to put it persistently" wording mentions .npmrc for pnpm
build-script controls, fix it.

## Files to edit

- research/research-npm-supply-chain-hardening.md
- guidelines/hardening-npm.md (verify, edit only if needed)

## Acceptance

- pnpm config-source description matches current pnpm docs.
- npm .npmrc description is unchanged (npm does read layered .npmrc).
- The doc does not imply npm and pnpm setting names or sources are
  interchangeable.
