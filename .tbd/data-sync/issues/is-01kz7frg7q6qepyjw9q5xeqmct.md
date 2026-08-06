---
type: is
id: is-01kz7frg7q6qepyjw9q5xeqmct
title: "VERIFY: npm 12 throws on unknown .npmrc/env configs - does the repo's NPM_CONFIG_* recipe break npm 12?"
kind: bug
status: closed
priority: 0
version: 2
labels:
  - research
dependencies: []
parent_id: is-01kz7f5sfqpzcjr0vnz1dk2qs1
created_at: 2026-08-04T22:54:26.039Z
updated_at: 2026-08-04T23:05:36.803Z
closed_at: 2026-08-04T23:05:36.802Z
close_reason: "VERIFIED, no breakage: npm 12 gates unknown-.npmrc-key errors behind strict-npmrc, which defaults to false. Only unknown CLI flags always error. The repo's env-var recipe is safe; documented the caveat to keep pnpm-only names in env rather than .npmrc or CLI flags."
---
npm 12 changed 'Unknown env config' from a warning to a thrown error. This repo's Step 1 exports NPM_CONFIG_FROZEN_LOCKFILE, NPM_CONFIG_MINIMUM_RELEASE_AGE, NPM_CONFIG_STRICT_DEP_BUILDS, which are pnpm-only names npm does not know. If env-supplied unknown configs also throw, every npm command breaks for anyone following this guide. Must verify and fix.
