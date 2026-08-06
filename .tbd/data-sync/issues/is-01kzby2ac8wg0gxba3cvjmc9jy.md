---
type: is
id: is-01kzby2ac8wg0gxba3cvjmc9jy
title: "PR #6 review F-4: .pth import detection should match site.py raw-line semantics"
kind: bug
status: closed
priority: 2
version: 3
labels: []
dependencies: []
parent_id: is-01kzby2767477gnba81a39t6fb
created_at: 2026-08-06T16:21:25.512Z
updated_at: 2026-08-06T16:40:46.733Z
closed_at: 2026-08-06T16:40:46.733Z
close_reason: "Fixed in 00ec171 on claude/supply-chain-hardn-review-62yhzw; per-finding details in each bead's notes and in the PR #6 disposition comment (issuecomment-5207516766). All 3 Bugbot threads replied + resolved. Validation: validate-docs OK, scanner tests 14/14, make format clean, 0 broken links/anchors."
---
scripts/audit_workspace.py:485 strips line before startswith('import '); CPython site.py tests the raw line, so indented import never executes. Drop strip or comment intentional over-approximation.

## Notes

DONE (pending commit): dropped .strip() so detection matches CPython site.py raw-line startswith(('import ','import\t')); comment explains indented import = path entry, never executed. Tests: pth raw import -> exit 3, indented-only -> exit 0, __editable__ -> INFO exit 1.
