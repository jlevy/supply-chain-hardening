---
type: is
id: is-01krfaht7djywhy0m0rvexg9f2
title: Pin scanner versions in CI examples and add missing test commands
kind: task
status: open
priority: 2
version: 1
labels:
  - docs
  - ci
dependencies: []
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:07:26.701Z
updated_at: 2026-05-13T00:07:26.701Z
---
# Pin scanner versions in CI examples; add cargo test --locked and go test ./... where missing

## Problem

CI YAML in the playbooks installs scanners from `latest` without
verification:

- `cargo install --locked cargo-audit && cargo audit`
- `go install golang.org/x/vuln/cmd/govulncheck@latest && govulncheck ./...`

Reviewer is correct that this is a small but real supply-chain risk in
the CI examples themselves. Also flagged: Rust CI examples lack
`cargo test --locked`; Go CI examples vary on whether they run `go test`.

## Fix

In CI YAML across all four playbooks:

- Use pinned versions for scanners (e.g. `govulncheck@v1.X.Y`,
  `cargo-audit --version <pin>`).
- Where the user-side install of a scanner uses the network at build time,
  add a note that an org should pre-install scanners into a hardened
  runner image. Provide both the quick recipe and the production-grade
  alternative.
- Add `cargo test --locked` to Rust CI examples (failure surface for
  malicious test fixtures).
- Ensure every Go CI example includes `go test ./...` so test-time code
  execution is at least observed under the hardened env vars.

## Files to edit

- guidelines/hardening-npm.md (CI section)
- guidelines/hardening-pypi.md (CI section)
- guidelines/hardening-crates.md (CI section)
- guidelines/hardening-go.md (CI section)
- research/* CI sections where they duplicate the operational guide

## Acceptance

- No CI example pulls a scanner from `@latest` without a comment noting
  this is the quick recipe and that orgs should pin.
- Rust CI has `--locked` on `cargo test`.
- Go CI runs `go test ./...` at least once under the hardening env.
