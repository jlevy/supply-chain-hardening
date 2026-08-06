---
type: is
id: is-01kzby28y7xe8fhj79f03cf023
title: "PR #6 review F-1: promote trigger classes to primary framing; retire L7"
kind: task
status: closed
priority: 2
version: 3
labels: []
dependencies: []
parent_id: is-01kzby2767477gnba81a39t6fb
created_at: 2026-08-06T16:21:24.039Z
updated_at: 2026-08-06T16:40:46.722Z
closed_at: 2026-08-06T16:40:46.722Z
close_reason: "Fixed in 00ec171 on claude/supply-chain-hardn-review-62yhzw; per-finding details in each bead's notes and in the PR #6 disposition comment (issuecomment-5207516766). All 3 Bugbot threads replied + resolved. Validation: validate-docs OK, scanner tests 14/14, make format clean, 0 broken links/anchors."
---
README.md layered model. Open-time is a trigger class, not an enforcement layer; its controls are L1/L5 at a new surface. Make trigger-class table primary, demote layers, drop L7.

## Notes

DONE (pending commit): README reworked. New '## Start Here' (trigger-class table primary map + Step 0 commands + audit_workspace + SUPPLY-CHAIN-SECURITY drop-in pointer); 'Quick Start' renamed 'Choosing Your Path'; '## The Layered Model (Where Enforcement Lives)' now opens with two-axes framing (trigger primary, layer secondary), L7 row deleted, L1 row extended with user/managed agent-editor settings, L5 row extended with pre-open triage, L7 bullet replaced with 'surface, not a seventh layer' bullet mapping to L1/L5, trigger->layer mapping table updated (Open-time -> L1 agent settings + L5 triage). 'stack of six layers' text now consistent.
