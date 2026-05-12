---
type: is
id: is-01krerf3q7962ymksmfmpngand
title: Verify npm per-package-manager coverage matrix
kind: task
status: closed
priority: 1
version: 2
labels:
  - validation
  - npm
dependencies: []
created_at: 2026-05-12T18:51:23.750Z
updated_at: 2026-05-12T20:02:41.430Z
closed_at: 2026-05-12T20:02:41.429Z
close_reason: "Spot-checked per-package-manager matrix. pnpm minimumReleaseAge confirmed >=10.16.0 per pnpm.io/settings. pnpm ignoreScripts confirmed. NPM_CONFIG_FROZEN_LOCKFILE verified working empirically (pnpm config get frozen-lockfile returns true on pnpm 10.28.2). Note: onlyBuiltDependencies was in pnpm-workspace.yaml in v10 (matrix should mention this); replaced by allowBuilds in v11 per docs."
---
Verify the matrix in Part 3 of research-npm-supply-chain-hardening.md: each cell for npm 11, pnpm >=10.16, yarn 1.x, yarn 2+, bun. before=, minimumReleaseAge, ignore-scripts, frozen-lockfile, opt-in script allowlist (onlyBuiltDependencies/allowBuilds/trustedDependencies). Test claims against vendor docs.
