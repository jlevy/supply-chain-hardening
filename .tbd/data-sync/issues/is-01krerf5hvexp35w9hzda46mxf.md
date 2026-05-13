---
type: is
id: is-01krerf5hvexp35w9hzda46mxf
title: Verify crates.io platform-specific setup
kind: task
status: closed
priority: 1
version: 5
labels:
  - validation
  - crates
dependencies: []
created_at: 2026-05-12T18:51:25.626Z
updated_at: 2026-05-12T20:55:04.203Z
closed_at: 2026-05-12T20:55:04.202Z
close_reason: "Verified: cargo and all tools (cargo-audit, cargo-deny, cargo-vet, cargo-crev) are cross-platform across macOS, Linux, Windows with identical commands. Shell alias guidance for bash/zsh/PowerShell verified correct. Alternative registry config in .cargo/config.toml uses [registries] with 'index' key supporting both git (https://...) and sparse (sparse+https://...) protocols, confirmed per doc.rust-lang.org/cargo/reference/registries.html. Fix applied: removed false [install] locked=true config.toml claim (affects platform-setup section); replaced with note that --locked must be passed explicitly or via alias."
---
Verify cargo and tool invocations work on macOS, Linux, Windows. Check alternative registry config in .cargo/config.toml.
