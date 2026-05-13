---
type: is
id: is-01krfafyy66yvkct59gaxx6e6s
title: Surface Go toolchain CVE (Step 0) and GOTOOLCHAIN=local in operational playbook
kind: task
status: closed
priority: 1
version: 3
labels:
  - correctness
  - go
dependencies: []
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:06:25.989Z
updated_at: 2026-05-13T01:27:46.935Z
closed_at: 2026-05-13T01:27:46.931Z
close_reason: "Added Step 0 to hardening-go.md: upgrade to Go 1.25.10 / 1.26.3 for CVE-2026-42501 (checksum DB bypass), regenerate go.sum from trusted sources, run go mod verify. Documented GOTOOLCHAIN=local as commented strict-mode option in the hardening script; explicit that it's defense-in-depth, not a substitute for the upgrade."
---
# Surface Go toolchain-proxy CVE (Step 0) and GOTOOLCHAIN=local option in operational playbook

## Problem

The research doc (research/research-go-supply-chain-hardening.md) covers the
2026 Go toolchain-proxy/checksum-bypass issue, but the short operational
playbook (guidelines/hardening-go.md) does not. Anyone copy-pasting only the
operational playbook may miss that:

- A specific Go version is required to pick up the fix.
- If they used an untrusted GOPROXY during the affected window, they need a
  remediation step (regenerate go.sum from trusted sources, run go mod
  verify).
- GOTOOLCHAIN=local is an option for teams that do not want automatic
  toolchain downloads (does not replace upgrading; it is a defense-in-depth
  control).

## Fix

Add to guidelines/hardening-go.md:

1. A new "Step 0: Keep the Go toolchain current" before Step 1 with:
   - The exact minimum Go version that includes the fix (verify against
     pkg.go.dev/vuln/ and Go release notes before committing).
   - A short note on when to regenerate go.sum from trusted sources and
     re-run `go mod verify` (i.e., if you used an untrusted proxy in the
     affected window).
2. In Step 1's hardening script, optionally export `GOTOOLCHAIN=local` for
   strict-mode environments, clearly labelled.
3. Make sure the operational playbook says the toolchain upgrade is the
   primary fix; GOTOOLCHAIN=local does not replace it.

## Files to edit

- guidelines/hardening-go.md

## Acceptance

- Reader of the short playbook alone sees the toolchain upgrade as Step 0.
- The doc names the exact minimum Go version after verification.
- GOTOOLCHAIN=local is described as defense-in-depth, not as a substitute.
