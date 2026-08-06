---
type: is
id: is-01kzby2at5b45645prrbxgz3x8
title: "PR #6 review F-5: document check_host() machine-wide scope"
kind: task
status: closed
priority: 2
version: 3
labels: []
dependencies: []
parent_id: is-01kzby2767477gnba81a39t6fb
created_at: 2026-08-06T16:21:25.957Z
updated_at: 2026-08-06T16:40:46.737Z
closed_at: 2026-08-06T16:40:46.737Z
close_reason: "Fixed in 00ec171 on claude/supply-chain-hardn-review-62yhzw; per-finding details in each bead's notes and in the PR #6 disposition comment (issuecomment-5207516766). All 3 Bugbot threads replied + resolved. Validation: validate-docs OK, scanner tests 14/14, make format clean, 0 broken links/anchors."
---
scripts/README.md: note host check inspects $HOME regardless of target path; optionally skip for non-cwd targets unless --only host.

## Notes

DONE (pending commit): check_host docstring + argparse epilog state host check inspects $HOME and is independent of PATH; scripts/README.md host bullet expanded with same note. No behavior change (kept: host artifacts are global).
