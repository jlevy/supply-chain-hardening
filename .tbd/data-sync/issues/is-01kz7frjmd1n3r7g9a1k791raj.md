---
type: is
id: is-01kz7frjmd1n3r7g9a1k791raj
title: "Validate: run tests/validate-docs.py and make format; fix any failures"
kind: task
status: closed
priority: 1
version: 3
labels:
  - docs
dependencies: []
parent_id: is-01kz7f5sfqpzcjr0vnz1dk2qs1
created_at: 2026-08-04T22:54:28.493Z
updated_at: 2026-08-04T23:15:28.228Z
closed_at: 2026-08-04T23:15:28.228Z
close_reason: "tests/validate-docs.py OK (31 env vars). make format (flowmark-rs 0.2.6) clean. audit_workspace.py verified on this repo and on a synthetic malicious repo (exit 3). Fixed a real portability bug found while validating: the byte-pattern grep used GNU-only \\| alternation while claiming BSD support; replaced with repeated -e."
---
