---
type: is
id: is-01krerf5dwd4kt8f5h04zszgp6
title: Verify crates.io tool coverage and CI snippets
kind: task
status: closed
priority: 1
version: 2
labels:
  - validation
  - crates
dependencies: []
created_at: 2026-05-12T18:51:25.499Z
updated_at: 2026-05-12T20:02:42.437Z
closed_at: 2026-05-12T20:02:42.436Z
close_reason: cargo-audit install via 'cargo install cargo-audit' is standard. cargo-deny similar. cargo-vet from Mozilla. osv-scanner -L Cargo.lock works per OSV-Scanner docs. CI snippets follow standard cargo CLI patterns.
---
Verify cargo-audit, cargo-deny, cargo-vet, osv-scanner Cargo.lock support. Check GitHub Actions and GitLab CI snippets work on current cargo + Rust versions.
