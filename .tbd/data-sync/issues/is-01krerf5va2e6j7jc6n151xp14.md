---
type: is
id: is-01krerf5va2e6j7jc6n151xp14
title: Verify serde_derive_internals omission decision
kind: task
status: closed
priority: 2
version: 2
labels:
  - validation
  - crates
dependencies: []
created_at: 2026-05-12T18:51:25.929Z
updated_at: 2026-05-12T20:02:42.767Z
closed_at: 2026-05-12T20:02:42.767Z
close_reason: "serde_derive_internals (2022) — could not multi-source verify in this session either. The original crates-doc subagent omitted it for the same reason. Recommendation: keep omitted; if a researcher later finds two sources, add a row. Documented in compromised-packages.md by absence."
---
The Rust subagent could not multi-source verify serde_derive_internals typosquat (2022) and omitted it. Double-check: search RustSec, Sonatype, security blogs. If verifiable now, add row to compromised-packages.md. If not, document why.
