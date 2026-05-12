---
type: is
id: is-01krerf55y8kkmy1p6jz1cpbav
title: Verify all crates.io incident rows in compromised-packages.md
kind: task
status: closed
priority: 1
version: 3
labels:
  - validation
  - crates
dependencies: []
created_at: 2026-05-12T18:51:25.245Z
updated_at: 2026-05-12T18:57:55.834Z
closed_at: 2026-05-12T18:57:55.833Z
close_reason: "Verified all 6 crates.io incident rows. Fixes applied: (1) rustdecimal vector changed from 'build.rs payload' to 'runtime payload in Decimal::new' in compromised-packages.md. (2) finch-rst/sha-rst sources corrected: removed incorrect Rust Blog reference (which covers finch-rust/sha-rust), added RUSTSEC-2025-0152 for finch_cli_rust, updated download count to ~61 combined. (3) All other rows (faster_log, evm-units, time-utility, mysten-metrics) verified against primary sources."
---
For each Rust row: rustdecimal (2022-05), faster_log+async_println (2025-09), evm-units+uniswap-utils (2025-12), finch-rst+sha-rst (2025-12), time-utility campaign (2026-02..03), mysten-metrics (2026-04). Verify dates, versions, scale, vector, references. Use RustSec advisory IDs.
