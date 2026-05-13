---
type: is
id: is-01krerf3q7962ymksmfmpngand
title: Verify npm per-package-manager coverage matrix
kind: task
status: closed
priority: 1
version: 5
labels:
  - validation
  - npm
dependencies: []
created_at: 2026-05-12T18:51:23.750Z
updated_at: 2026-05-12T20:55:13.217Z
closed_at: 2026-05-12T20:55:13.216Z
close_reason: "Verified per-package-manager coverage matrix against vendor docs. Found and fixed 5 discrepancies: (1) npm 11 minimumReleaseAge row was 'warns and ignores' but npm 11.10+ ships min-release-age (days); corrected. (2) yarn 2+ row was blank for rolling release-age but yarn berry >=4.10 has npmMinimalAgeGate (minutes); added. (3) bun row was blank for rolling release-age but bun supports minimumReleaseAge in bunfig.toml (seconds); added. (4) pnpm 11 allowBuilds shown as array but is actually a map {name: bool}; corrected code sample and matrix cell. (5) yarn berry has npmPreapprovedPackages for opt-in script allowlist; added to matrix. Also fixed fish shell recipe missing GNU date fallback for Linux users. Citations: pnpm.io/settings, pnpm.io/blog/releases/11.0, pnpm.io/migration, docs.npmjs.com/cli/v11/using-npm/config, yarnpkg.com/configuration/yarnrc, socket.dev/blog/npm-introduces-minimumreleaseage, mondoo.com/blog/npm-supply-chain-security-package-manager-defenses-2026, bun.com/docs/guides/install/trusted"
---
Verify the matrix in Part 3 of research-npm-supply-chain-hardening.md: each cell for npm 11, pnpm >=10.16, yarn 1.x, yarn 2+, bun. before=, minimumReleaseAge, ignore-scripts, frozen-lockfile, opt-in script allowlist (onlyBuiltDependencies/allowBuilds/trustedDependencies). Test claims against vendor docs.
