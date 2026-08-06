---
type: is
id: is-01kz7m7syqbw5686fhcacrdqzn
title: "Simplify: retire the date -v-14d shell hack for npm 11.10+ (min-release-age is a rolling window)"
kind: task
status: closed
priority: 1
version: 2
labels:
  - docs
dependencies: []
parent_id: is-01kz7m5v8k3y8kvwdkqn6gw87g
created_at: 2026-08-05T00:12:41.815Z
updated_at: 2026-08-05T00:14:58.823Z
closed_at: 2026-08-05T00:14:58.823Z
close_reason: npm 11.10+ min-release-age is a rolling window, so the BSD/GNU date arithmetic is now a labelled legacy fallback (block B, commented out) rather than the default. New Step 0 leads with 'npm config set min-release-age 14 --location=user'.
---
