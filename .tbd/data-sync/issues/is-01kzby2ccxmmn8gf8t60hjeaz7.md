---
type: is
id: is-01kzby2ccxmmn8gf8t60hjeaz7
title: "PR #6 review S-3: self-enforcing stale-date/version-drift check"
kind: task
status: closed
priority: 2
version: 3
labels: []
dependencies: []
parent_id: is-01kzby2767477gnba81a39t6fb
created_at: 2026-08-06T16:21:27.581Z
updated_at: 2026-08-06T16:40:46.753Z
closed_at: 2026-08-06T16:40:46.753Z
close_reason: "Fixed in 00ec171 on claude/supply-chain-hardn-review-62yhzw; per-finding details in each bead's notes and in the PR #6 disposition comment (issuecomment-5207516766). All 3 Bugbot threads replied + resolved. Validation: validate-docs OK, scanner tests 14/14, make format clean, 0 broken links/anchors."
---
Tiny check (validate-docs.py or CI) that greps for stale dates/version drift so F-6 is self-enforcing.

## Notes

TODO: extend tests/validate-docs.py with dated-stamp policy check: explicit allow-set of files that may carry '**Last updated:**' (playbooks, research, compromised-packages, self-update-instructions, audit-log template); flag stamps elsewhere and missing stamps on dated pages. Also covers F-6 enforcement.
