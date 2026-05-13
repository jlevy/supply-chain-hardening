---
type: is
id: is-01krerf5dwd4kt8f5h04zszgp6
title: Verify crates.io tool coverage and CI snippets
kind: task
status: closed
priority: 1
version: 5
labels:
  - validation
  - crates
dependencies: []
created_at: 2026-05-12T18:51:25.499Z
updated_at: 2026-05-12T20:54:59.927Z
closed_at: 2026-05-12T20:54:59.926Z
close_reason: "Verified: cargo-audit install via 'cargo install --locked cargo-audit' confirmed (crates.io 7.4M+ downloads). cargo-deny 'cargo deny init' generates deny.toml, 'cargo deny check' runs all checks, confirmed at embarkstudios.github.io/cargo-deny. cargo-vet attestations via 'cargo vet certify' confirmed. osv-scanner Cargo.lock support confirmed. Fix applied: updated all 'osv-scanner -L Cargo.lock' to V2 syntax 'osv-scanner scan -L Cargo.lock' (3 occurrences in research doc, 1 in hardening doc). GitHub Actions snippet verified correct (actions/checkout@v4, dtolnay/rust-toolchain@stable). GitLab CI snippet verified correct (rust:latest image, cargo build --locked)."
---
Verify cargo-audit, cargo-deny, cargo-vet, osv-scanner Cargo.lock support. Check GitHub Actions and GitLab CI snippets work on current cargo + Rust versions.
