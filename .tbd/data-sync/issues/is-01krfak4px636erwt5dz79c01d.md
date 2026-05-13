---
type: is
id: is-01krfak4px636erwt5dz79c01d
title: Add SECURITY_MODEL.md describing the layered defense model (L1-L6)
kind: feature
status: open
priority: 2
version: 1
labels:
  - docs
  - architecture
dependencies: []
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:08:10.204Z
updated_at: 2026-05-13T00:08:10.204Z
---
# Add SECURITY_MODEL.md describing the layered defense model

## Problem

Reviewer proposes a six-layer model (developer defaults / project policy /
CI gates / org registry-proxy / sandbox / IR) and recommends a
docs/SECURITY_MODEL.md as a top-level orientation doc.

The current repo is heavy on Layer 1 (developer defaults via shell init)
and touches Layers 2-3 (project lockfiles, CI gates) without naming the
layers as a stack. Layers 4-6 are mostly absent.

## Senior judgment

- **Layer 4 (org registry/proxy)** is explicitly out of scope in the PyPI
  research doc and would substantially expand the repo's mission. Mention
  it as a recommended team posture; do not write Artifactory/Nexus setup
  guides.
- **Layer 5 (sandbox for untrusted repos)** is in scope and important;
  agents running in this repo's CLAUDE.md / AGENTS.md flows are exactly
  the at-risk population. This deserves a short procedure (see related
  untrusted-repo bead).
- **Layer 6 (incident response)** is already partially present in each
  playbook's "If You Have Hits" section. SECURITY_MODEL.md can link to
  those rather than duplicate.

## Fix

Create SECURITY_MODEL.md at repo root (or under guidelines/) with:

1. Short table of layers (1-6), one sentence each, with a "where it lives"
   pointer:
   - L1 Developer defaults -> guidelines/hardening-*.md
   - L2 Project policy -> linked per-ecosystem subsections (uv.lock, npm
     ci, Cargo.lock, go.sum, etc.)
   - L3 CI enforcement -> "CI Enforcement" sections in each playbook
   - L4 Org registry/proxy -> short paragraph + external pointers; mark
     "out of scope for hands-on guidance"
   - L5 Untrusted-repo sandbox -> link to new sandbox-procedure doc
   - L6 Incident response -> "If You Have Hits" sections + audit log
     template
2. Explicit framing: this repo's primary contribution is L1-L3 plus
   strong L6. L4-L5 are documented just enough that a team knows what
   is missing.

Link from README.md "What This Repo Is" section.

## Files to edit / create

- New: SECURITY_MODEL.md
- README.md: add a section pointer
- AGENTS.md: link to it from "Safety Rule For Agents"

## Acceptance

- A reader unfamiliar with supply-chain hardening can identify which
  controls live where in 60 seconds.
- The doc is honest about scope: does not promise hands-on Artifactory
  setup, does promise sandbox guidance.
