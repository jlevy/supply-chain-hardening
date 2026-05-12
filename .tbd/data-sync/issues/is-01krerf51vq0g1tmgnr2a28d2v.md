---
type: is
id: is-01krerf51vq0g1tmgnr2a28d2v
title: Verify crates.io Part 1 background and severity assessment
kind: task
status: closed
priority: 1
version: 3
labels:
  - validation
  - crates
dependencies: []
created_at: 2026-05-12T18:51:25.114Z
updated_at: 2026-05-12T18:55:30.993Z
closed_at: 2026-05-12T18:55:30.988Z
close_reason: "Verified Part 1 background. Design properties (immutable versions, SHA-256, no install scripts, build.rs gap, single registry, cargo install re-resolve) all confirmed against cargo docs and RustSec. Sonatype 454,600 and Snyk npm 3000+/PyPI 600+ figures confirmed. Discrepancy: doc claims '5-10 confirmed malicious crate removals per year 2022-2025' but RustSec shows 2023=7, 2025=15, 2026(YTD)=32+. Also: compromised-packages.md rustdecimal row says 'build.rs payload' but attack was runtime code in Decimal::new."
---
Fact-check Part 1 of research-crates-supply-chain-hardening.md: cargo design properties (immutable, checksums, no install scripts, build.rs surface), 'How Big Is This Problem?' assessment claims (single-digit incidents/year vs npm thousands). Cross-reference RustSec, Snyk, Sonatype reports.
