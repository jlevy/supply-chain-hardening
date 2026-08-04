---
type: is
id: is-01kz7jj5t5wqmq3w02g64kd3q1
title: "Research: ecosystem-shipped cool-off defaults + expert guidance since 2026-05"
kind: task
status: closed
priority: 0
version: 2
labels:
  - research
dependencies: []
created_at: 2026-08-04T23:43:24.469Z
updated_at: 2026-08-04T23:46:27.287Z
closed_at: 2026-08-04T23:46:27.287Z
close_reason: "Verified from vendor docs. Defaults: pnpm 11 = 1440min ON; Yarn 4.10+ npmMinimalAgeGate = '1w' ON; Bun 1.3+ minimumReleaseAge = 259200s (3d) ON; npm 12 min-release-age = null OPT-IN; uv and pip = OPT-IN; Dependabot cooldown.default-days = 3 ON (version updates only, security exempt); Renovate = OPT-IN. Secondary blogs (craigory.dev) were stale on Yarn/Bun; vendor docs used."
---
Answer: (1) which package managers now ship a DEFAULT minimum release age (npm 12, pnpm 11, uv, bun, yarn, pip) vs merely supporting one; (2) registry-side responses (npm token/trusted-publishing changes, PyPI); (3) bot-side cooldown support (Dependabot, Renovate); (4) expert/consortium guidance published since the last refresh. Then check what the repo already covers.
