---
type: is
id: is-01kzby29ffx7qp8w32e4ppzg14
title: "PR #6 review F-2: cap the incident table; stop becoming a feed"
kind: task
status: closed
priority: 2
version: 3
labels: []
dependencies: []
parent_id: is-01kzby2767477gnba81a39t6fb
created_at: 2026-08-06T16:21:24.590Z
updated_at: 2026-08-06T16:40:46.725Z
closed_at: 2026-08-06T16:40:46.725Z
close_reason: "Fixed in 00ec171 on claude/supply-chain-hardn-review-62yhzw; per-finding details in each bead's notes and in the PR #6 disposition comment (issuecomment-5207516766). All 3 Bugbot threads replied + resolved. Validation: validate-docs OK, scanner tests 14/14, make format clean, 0 broken links/anchors."
---
compromised-packages.md: 41 rows and growing. Split actively-scanned vs recognize-historically (no per-version IOCs), point live-feed at OSV/GHSA/Aikido, update scope note and self-update cadence.

## Notes

DONE (pending commit): compromised-packages.md: Scope gains Aging paragraph (12-month cap unless artifacts still served); 'Table (Actionable IOCs)' -> 'Active Watch List (Actionable IOCs)' (33 rows); 9 pre-2025-08 rows (BoltDB, rustdecimal, ctx, torchtriton, Ultralytics, hypert/layout, fake x/crypto, disk-wiper, qmgo) moved to new '## Historical Incidents (Recognition Only)' compact table (no per-version IOCs, 1-2 primary refs); How To Use updated (osv-scanner for old lockfiles); Contextual promote wording; date bumped 2026-08-06. self-update-instructions.md: three-section description + aging-out procedure. README maintenance cadence row updated.
