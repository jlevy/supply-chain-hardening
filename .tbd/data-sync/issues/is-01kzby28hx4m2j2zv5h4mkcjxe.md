---
type: is
id: is-01kzby28hx4m2j2zv5h4mkcjxe
title: "PR #6 review B3: .codex/ omitted from triage docs and CI path guard"
kind: bug
status: closed
priority: 2
version: 3
labels: []
dependencies: []
parent_id: is-01kzby2767477gnba81a39t6fb
created_at: 2026-08-06T16:21:23.645Z
updated_at: 2026-08-06T16:40:46.719Z
closed_at: 2026-08-06T16:40:46.719Z
close_reason: "Fixed in 00ec171 on claude/supply-chain-hardn-review-62yhzw; per-finding details in each bead's notes and in the PR #6 disposition comment (issuecomment-5207516766). All 3 Bugbot threads replied + resolved. Validation: validate-docs OK, scanner tests 14/14, make format clean, 0 broken links/anchors."
---
AGENTS.md:51-57, guidelines/hardening-agent-workspaces.md:49-59,314-316. PR adds .codex/hooks.json but triage lists, attack-surface table, and sample CI path guard omit .codex/.

## Notes

DONE (pending commit): (1) scanner: check_autostart now reads .codex/hooks.json via same loop as .claude settings (same hook schema); verified on this repo: 8 HIGH (4 claude + 4 codex). (2) docs: AGENTS.md rule 6; hardening-agent-workspaces.md attack-surface table row, triage ls/cat/grep + git log, compromise find, IR step 4, CI guard regex (\.codex/), CODEOWNERS list, new Codex note end of Step 2; hardening-ci-cd.md CODEOWNERS; untrusted-repo-first-run.md editor/agent row; hardening-npm.md + hardening-pypi.md IR step 4; scripts/README.md; self-update-instructions.md maintenance note. Test: test_codex_hooks.
