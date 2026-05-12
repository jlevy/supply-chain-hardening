---
type: is
id: is-01krerf6vnwvr2rytgegpf671x
title: Cross-verify compromised-packages.md row consistency
kind: task
status: closed
priority: 2
version: 2
labels:
  - validation
  - cross-cutting
dependencies: []
created_at: 2026-05-12T18:51:26.964Z
updated_at: 2026-05-12T20:01:16.809Z
closed_at: 2026-05-12T20:01:16.809Z
close_reason: "Cross-checked compromised-packages.md table rows against package@version mentions in all 4 research docs. Findings: research-npm references safe-downgrade versions (chalk@5.6.0, debug@4.4.1, axios@1.14.0) consistent with the bad versions in the table (chalk@5.6.1, debug@4.4.2, axios@1.14.1). TanStack @tanstack/react-router@1.169.9 (patched) matches table notation. mysten-metrics@9.0.3 (crates) and rustdecimal@1.23.1 (crates) match their respective table rows. Table chronological order preserved across all 26 rows. No drift detected. Note: Go validation agent appears to have updated MongoDB qmgo date from 2025-05 to 2025-06 during its incident verification (sch-po93), which is now consistent in the table."
---
Cross-check every row in compromised-packages.md against the ecosystem-specific research doc that references it. Look for: missing rows, version-number drift, reference-URL changes, date discrepancies. Update both as needed.
