---
type: is
id: is-01kzby2b7batargrm92c5ppxmv
title: "PR #6 review F-6: reserve dated stamps for currency-sensitive pages"
kind: task
status: closed
priority: 2
version: 3
labels: []
dependencies: []
parent_id: is-01kzby2767477gnba81a39t6fb
created_at: 2026-08-06T16:21:26.378Z
updated_at: 2026-08-06T16:40:46.741Z
closed_at: 2026-08-06T16:40:46.741Z
close_reason: "Fixed in 00ec171 on claude/supply-chain-hardn-review-62yhzw; per-finding details in each bead's notes and in the PR #6 disposition comment (issuecomment-5207516766). All 3 Bugbot threads replied + resolved. Validation: validate-docs OK, scanner tests 14/14, make format clean, 0 broken links/anchors."
---
Uniform Last updated: 2026-08-04 across all docs hides which pages rot. Keep verified-against stamps on incident/version/playbook pages; drop from evergreen methodology pages.

## Notes

IN PROGRESS: README header 'Last updated' removed (evergreen); policy note added to self-update-instructions.md (dated stamps only on currency pages; validate-docs enforces). REMAINING: remove Last updated line from guidelines/strict-mode.md and guidelines/untrusted-repo-first-run.md; add DATED_DOCS enforcement check to tests/validate-docs.py (with S-3); keep stamps on playbooks/research/compromised-packages/self-update.
