---
type: is
id: is-01kz7m7thjrwyvbya0t9b2j5rz
title: "Simplify: drop pnpm-10-only env vars from the default recipe (pnpm 11 ignores them)"
kind: task
status: closed
priority: 1
version: 2
labels:
  - docs
dependencies: []
parent_id: is-01kz7m5v8k3y8kvwdkqn6gw87g
created_at: 2026-08-05T00:12:42.417Z
updated_at: 2026-08-05T00:14:59.535Z
closed_at: 2026-08-05T00:14:59.535Z
close_reason: NPM_CONFIG_FROZEN_LOCKFILE and NPM_CONFIG_STRICT_DEP_BUILDS are now grouped and labelled pnpm-10.x-only with an explicit skip instruction, since npm ignores them and pnpm 11 neither reads NPM_CONFIG_* nor needs strictDepBuilds set.
---
