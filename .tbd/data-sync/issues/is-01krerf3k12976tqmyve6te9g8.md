---
type: is
id: is-01krerf3k12976tqmyve6te9g8
title: Verify npm four-control hardening pattern semantics
kind: task
status: closed
priority: 1
version: 3
labels:
  - validation
  - npm
dependencies: []
created_at: 2026-05-12T18:51:23.616Z
updated_at: 2026-05-12T18:59:47.178Z
closed_at: 2026-05-12T18:59:47.177Z
close_reason: "Verified four-control semantics. (1) NPM_CONFIG_BEFORE: works as described for both npm (docs.npmjs.com/cli/v11/using-npm/config) and pnpm. (2) NPM_CONFIG_MINIMUM_RELEASE_AGE: pnpm 10.16.0+ confirmed (pnpm.io/blog/releases/10.16, released 2025-09-12). Fixed: npm 11.10+ now ships min-release-age (different name, units in days not minutes); updated Control 2 section. (3) NPM_CONFIG_IGNORE_SCRIPTS: confirmed for both npm and pnpm. (4) NPM_CONFIG_FROZEN_LOCKFILE: confirmed pnpm-only; npm has no env var equivalent, use npm ci. Config precedence (env > project rc > user rc > global) confirmed at docs.npmjs.com/cli/v11/configuring-npm/npmrc."
---
Verify NPM_CONFIG_BEFORE, NPM_CONFIG_MINIMUM_RELEASE_AGE (pnpm 10.16.0+), NPM_CONFIG_IGNORE_SCRIPTS, NPM_CONFIG_FROZEN_LOCKFILE work as described. Test against current pnpm 10.x and 11.x docs at pnpm.io/settings. Verify config precedence (env > project rc > user rc > global).
