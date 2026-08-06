---
type: is
id: is-01kzby27rqc9qxwmr7bfznevee
title: "PR #6 review B1: unicode scan globs miss .agents/skills/**/*.md"
kind: bug
status: closed
priority: 2
version: 3
labels: []
dependencies: []
parent_id: is-01kzby2767477gnba81a39t6fb
created_at: 2026-08-06T16:21:22.839Z
updated_at: 2026-08-06T16:40:46.703Z
closed_at: 2026-08-06T16:40:46.698Z
close_reason: "Fixed in 00ec171 on claude/supply-chain-hardn-review-62yhzw; per-finding details in each bead's notes and in the PR #6 disposition comment (issuecomment-5207516766). All 3 Bugbot threads replied + resolved. Validation: validate-docs OK, scanner tests 14/14, make format clean, 0 broken links/anchors."
---
scripts/audit_workspace.py:94-100. Bugbot: unicode check lists .claude/skills/**/*.md but not .agents/skills/**/*.md though this PR adds .agents/skills/tbd/SKILL.md. TrapDoor-style hidden Unicode there would be missed.

## Notes

DONE (pending commit): added .agents/**/*.md to AGENT_INSTRUCTION_GLOBS in scripts/audit_workspace.py; updated scripts/README.md unicode description; regression test test_unicode_in_agents_skills in tests/test_audit_workspace.py passes (U+200B in .agents/skills/helper/SKILL.md -> HIGH, exit 3).
