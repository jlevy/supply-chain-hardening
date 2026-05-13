---
type: is
id: is-01krfamp3a8kckmzq8687fcfy2
title: Split compromised-packages.md into actionable IOCs and contextual incidents
kind: task
status: open
priority: 3
version: 1
labels:
  - docs
  - watch-list
dependencies: []
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:09:00.777Z
updated_at: 2026-05-13T00:09:00.777Z
---
# Separate "confirmed actionable IOCs" from "contextual incidents" in compromised-packages.md

## Problem

compromised-packages.md mixes incidents that yield exact `pkg@version`
IOCs grep-able in lockfiles with incidents that are mostly context
(e.g., "unspecified versions, named campaign"). Reviewer recommends two
sections so a defender running an actionable scan does not waste cycles
on rows with nothing to grep.

## Fix

In compromised-packages.md:

- Keep the main "Table" for rows with exact package names + versions +
  references.
- Add a new section "Contextual Incidents" for items with named
  campaigns but no actionable grep target. State explicitly: "These
  rows describe campaigns and patterns but are not grep-able. Use the
  authoritative-sources feeds for live tracking."

Note: this overlaps with the "pending-citation rows" bead. If we
complete those citations, they may move from "Contextual" back to the
canonical table. The two beads are sequential: first verify pending
rows; then split the rest.

## Files to edit

- compromised-packages.md

## Acceptance

- Anyone running a scan sees only actionable rows in the main table.
- Campaign-level context is preserved for readers who want it.
- self-update-instructions.md "Updating compromised-packages.md"
  procedure is updated to reflect the two-section model.

## Dependency

Depends on the pending-citation cleanup bead so we are not splitting
the same rows twice.
