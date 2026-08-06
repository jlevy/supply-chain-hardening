---
type: is
id: is-01kzby2a0ry659ppbk446y3mtc
title: "PR #6 review F-3: rename Ten-Minute Setup; separate happy path from edge cases"
kind: task
status: closed
priority: 2
version: 3
labels: []
dependencies: []
parent_id: is-01kzby2767477gnba81a39t6fb
created_at: 2026-08-06T16:21:25.143Z
updated_at: 2026-08-06T16:40:46.729Z
closed_at: 2026-08-06T16:40:46.729Z
close_reason: "Fixed in 00ec171 on claude/supply-chain-hardn-review-62yhzw; per-finding details in each bead's notes and in the PR #6 disposition comment (issuecomment-5207516766). All 3 Bugbot threads replied + resolved. Validation: validate-docs OK, scanner tests 14/14, make format clean, 0 broken links/anchors."
---
guidelines/hardening-npm.md:32 and other playbooks. Rename heading, make Step 0 the literal short path, hard Advanced/only-if boundary before version-specific edge cases.

## Notes

IN PROGRESS: hardening-npm.md done: '## Hardening (Ten-Minute Setup)' -> '## Setup'; Step 0 retitled 'The Ten-Minute Setup'; Agent Ban List moved up into Setup; new '## Advanced Setup: Only If You Need It' boundary with per-step routing (Steps 1-3 CI/inheritance/older tools, Step 4 fresh-package day, Step 5 upgrade-time); old ban-list position removed; Bun box ref now 'in the Setup section above'. REMAINING: rename '## Hardening (Ten-Minute Setup)' -> '## Setup' in hardening-pypi.md:25, hardening-crates.md:12, hardening-go.md:12, hardening-agent-workspaces.md:67; update AGENTS.md line 17 'Apply the Ten-Minute Setup verbatim' -> Setup section; bump Last updated on materially edited playbooks (npm, agent-workspaces, pypi, ci-cd, untrusted 2026-08-06); README refs already updated.
