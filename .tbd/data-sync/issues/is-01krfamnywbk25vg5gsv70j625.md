---
type: is
id: is-01krfamnywbk25vg5gsv70j625
title: Add 'Last verified against package-manager versions' table and maintenance checklist
kind: task
status: closed
priority: 3
version: 3
labels:
  - maintenance
  - docs
dependencies: []
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:09:00.635Z
updated_at: 2026-05-13T01:41:31.452Z
closed_at: 2026-05-13T01:41:31.447Z
close_reason: Created MAINTENANCE.md with 'Last Verified Against' table (npm 11.x, pnpm 10.x, pip 26.1, uv latest, cargo 1.83+, go 1.25.10/1.26.3) and a six-step Re-Verify On Major-Version Bump checklist that pairs with tests/validate-docs.py. Linked from README.md Maintaining section. Cross-referenced from self-update-instructions.md.
---
# Add "Last verified against package-manager versions" table and maintenance checklist

## Problem

The docs cite specific versions ("pip >=26.1", "pnpm >= 10.16.0",
"Poetry >= 2.4.0") in scattered places. Reviewer suggests a single table
listing the package-manager versions the docs are validated against,
plus a maintenance checklist for re-verifying when those tools release
major versions.

## Fix

In README.md (or a new MAINTENANCE.md):

```
| Tool | Last verified version | Date | Validator |
| --- | --- | --- | --- |
| npm | x.y.z | YYYY-MM-DD | <author> |
| pnpm | x.y.z | ... | ... |
| pip | x.y.z | ... | ... |
| uv | x.y.z | ... | ... |
| cargo | x.y.z | ... | ... |
| go | x.y.z | ... | ... |
```

Add to self-update-instructions.md:

- A "Re-verify on major-version bump" checklist for each package
  manager: which env vars to re-check, which docs pages to re-read.
- A pointer to the doc-lint CI job (from related bead) and to the
  per-ecosystem env-var allow-list.

## Files to edit

- README.md or new MAINTENANCE.md
- self-update-instructions.md

## Acceptance

- A future maintainer can identify within 30 seconds which tool
  versions the docs were last validated against.
- The maintenance checklist references the doc-lint job and the
  allow-list location.
