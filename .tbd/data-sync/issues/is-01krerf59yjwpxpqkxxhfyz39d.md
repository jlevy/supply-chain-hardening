---
type: is
id: is-01krerf59yjwpxpqkxxhfyz39d
title: Verify crates.io hardening pattern
kind: task
status: closed
priority: 1
version: 7
labels:
  - validation
  - crates
dependencies: []
created_at: 2026-05-12T18:51:25.373Z
updated_at: 2026-05-12T20:54:54.892Z
closed_at: 2026-05-12T20:54:54.888Z
close_reason: "Verified: cargo --locked confirmed valid for build/install/run/test per doc.rust-lang.org/cargo. cargo-audit (RustSec-backed, v0.21+) confirmed at crates.io/crates/cargo-audit. cargo-deny (EmbarkStudios, v0.19.5) confirmed; deny.toml [sources] allow-registry URL 'https://github.com/rust-lang/crates.io-index' matches upstream template. cargo-vet (mozilla/cargo-vet v0.10.0) confirmed; 'cargo vet certify' and 'cargo vet import' commands verified against mozilla.github.io/cargo-vet/commands.html. build.rs review guidance aligns with RustSec and Rust Foundation recommendations. Fix applied: removed false claim that [install] locked=true exists in ~/.cargo/config.toml (no such stable config key per doc.rust-lang.org/cargo/reference/config.html); replaced with shell-alias-only guidance. Also fixed cargo vet import example URL branch (master->main)."
---
Verify cargo --locked, Cargo.lock enforcement, cargo-audit (RustSec), cargo-deny policy, cargo-vet attestations, build.rs review. Cross-check against current Rust Foundation security guidance and cargo docs.
