---
type: is
id: is-01kzby2859emws369efp61fqqz
title: "PR #6 review B2: JSONC trailing commas downgrade HIGH autostart finding"
kind: bug
status: closed
priority: 2
version: 3
labels: []
dependencies: []
parent_id: is-01kzby2767477gnba81a39t6fb
created_at: 2026-08-06T16:21:23.240Z
updated_at: 2026-08-06T16:40:46.715Z
closed_at: 2026-08-06T16:40:46.715Z
close_reason: "Fixed in 00ec171 on claude/supply-chain-hardn-review-62yhzw; per-finding details in each bead's notes and in the PR #6 disposition comment (issuecomment-5207516766). All 3 Bugbot threads replied + resolved. Validation: validate-docs OK, scanner tests 14/14, make format clean, 0 broken links/anchors."
---
scripts/audit_workspace.py:165-213,238-285. load_jsonc strips comments then strict json.loads rejects trailing commas VS Code allows; runOn:folderOpen task in valid JSONC becomes INFO parse-failure, exit 1 not 3.

## Notes

DONE (pending commit): load_jsonc now strips trailing commas outside strings after comment removal (second look-back pass on closers); malicious JSONC tasks.json with comments+trailing commas -> HIGH folderOpen finding, exit 3; truly malformed JSON still degrades to INFO could-not-parse. Tests: test_jsonc_trailing_commas, test_malformed_json_still_reported.
