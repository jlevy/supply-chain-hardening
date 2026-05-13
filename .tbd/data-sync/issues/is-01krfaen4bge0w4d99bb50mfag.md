---
type: is
id: is-01krfaen4bge0w4d99bb50mfag
title: Move pending-citation rows out of canonical compromised-packages table
kind: bug
status: closed
priority: 1
version: 4
labels:
  - correctness
  - watch-list
dependencies:
  - type: blocks
    target: is-01krfamp3a8kckmzq8687fcfy2
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:05:43.178Z
updated_at: 2026-05-13T01:25:34.212Z
closed_at: 2026-05-13T01:25:34.203Z
close_reason: Removed 'pending direct citation' rows from canonical table. Created new 'Unverified / Pending Verification' section listing the two Aqua Trivy / Bitwarden CLI items with what is known vs missing. Canonical table now only contains rows with exact pkg@version, dates, and multi-source references.
---
# Move "pending direct citation" rows out of canonical compromised-packages table

## Problem

compromised-packages.md is described as a "curated watch list" of confirmed,
multi-source-verified incidents. Two rows currently fail that bar:

- "2026-03 Aqua Trivy compromise" - "StepSecurity (pending direct citation)"
- "2026-04 Bitwarden CLI" - "TeamPCP actor / StepSecurity (pending direct
  citation)"

Both have unspecified affected versions and no concrete IOC string to grep
for. They cannot drive any action.

Reviewer's correct point: a canonical watch list must never include "pending
direct citation" as a final state. Either verify and complete, or move to a
separate non-canonical notes section.

## Fix

Two options:

1. **Best**: Find the citations, fill in exact package@version, dates, and
   sources. If verification succeeds against at least two independent
   Tier-2 sources per self-update-instructions.md, keep them in the canonical
   table.
2. **Acceptable**: Create a new section in compromised-packages.md titled
   "Unverified / Pending Verification" with these rows. Make clear that the
   canonical "Table" section is for actionable IOCs only. State what is
   missing for each unverified row.

Prefer option 1 if a researcher cycle of 30-60 minutes resolves both. If not,
option 2.

## Files to edit

- compromised-packages.md

## Acceptance

- The main "Table" section contains only rows where every column has a
  concrete value and at least two references are listed.
- Any unverified-but-noteworthy items live in a clearly-labeled separate
  section (or are removed).
- self-update-instructions.md "Updating compromised-packages.md" procedure is
  consistent with whatever policy is chosen.

## Dependency note

This bead is independent of the others and can be done first.
