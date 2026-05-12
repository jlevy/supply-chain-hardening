# crates.io Operational Hardening

**Last updated:** 2026-05-12

**Author:** Joshua Levy (github.com/jlevy) and LLM assistance

The minimum action list to harden a workstation or CI runner against crates.io
supply-chain attacks, and to check whether you have already been compromised.
Full threat model, per-platform setup, IOC feeds, and scanning tools in
[research-crates-supply-chain-hardening.md](../research/research-crates-supply-chain-hardening.md).

## Hardening (Ten-Minute Setup)

### Step 1: Always Use `--locked`

The single most impactful habit: pass `--locked` to every `cargo install`,
`cargo build`, and `cargo run` invocation.
This forces Cargo to use the committed `Cargo.lock` rather than re-resolving
dependencies, which could pull in a newly published malicious version.

```sh
cargo build --locked
cargo install --locked some-tool
cargo run --locked
```

Without `--locked`, `cargo install` ignores the packaged `Cargo.lock` entirely and
re-resolves from scratch.

### Step 2: Commit `Cargo.lock` (For Applications And Binaries)

Libraries traditionally gitignore `Cargo.lock`. Applications and binaries should commit
it. A committed lockfile combined with `--locked` pins the exact dependency tree the
author tested.

### Step 3: Install `cargo-audit` And `cargo-deny`

```sh
cargo install --locked cargo-audit
cargo install --locked cargo-deny
```

Run both against every project:

```sh
# Check for known vulnerabilities (RustSec advisory DB)
cargo audit

# Policy-as-code: ban specific versions, license families, duplicate deps, sources
cargo deny check
```

`cargo deny` requires a `deny.toml` config file.
Generate a starter:

```sh
cargo deny init
```

### Step 4: Install `cargo-vet` (Optional, Recommended For Teams)

```sh
cargo install --locked cargo-vet
cargo vet init
cargo vet
```

`cargo-vet` (Mozilla) records audit entries certifying that a human reviewed a crate
version. Teams share audit logs so each crate only needs review once across the
organization.

### Step 5: Verify

```sh
cargo audit                  # no advisories
cargo deny check             # all checks pass
cargo vet                    # all dependencies vetted or exempted
```

### Step 6: When You Intentionally Need An Unvetted Crate

Explicitly exempt it in `cargo-vet`:

```sh
cargo vet certify <crate> <version>
```

Or add a temporary exemption in `supply-chain/config.toml`.

## Compromise Assessment

### Step 1: Scan Every Lockfile

```sh
# Install once: https://github.com/google/osv-scanner/releases
osv-scanner scan -L Cargo.lock

# Or scan recursively:
osv-scanner scan source -r .

# RustSec-specific:
cargo audit
```

### Step 2: Grep For Known IOCs From The Most Recent Named Attacks

The most relevant crates.io attacks as of 2026-05-12. The cross-ecosystem table is in
[`compromised-packages.md`](../compromised-packages.md); this is the crates.io
quick-grep extract:

| Date | Name | Quick IOC Pattern |
| --- | --- | --- |
| 2026-04 | mysten-metrics | `mysten-metrics@9.0.3` |
| 2026-02/03 | Time-utility campaign | `chrono_anchor`, `dnp3times`, `time_calibrator`, `time_calibrators`, `time-sync` |
| 2025-12 | evm-units / uniswap-utils | `evm-units` (all versions by user `ablerust`), `uniswap-utils` (all versions) |
| 2025-12 | finch-rst / sha-rst | `finch-rst`, `sha-rst`, `finch_cli_rust` |
| 2025-09 | faster_log / async_println | `faster_log` (all versions by user `rustguruman`), `async_println` |
| 2022-05 | rustdecimal | `rustdecimal@1.23.1` |

Quick grep template:

```sh
#!/usr/bin/env bash
# Usage: scan-crate-iocs.sh Cargo.lock  crate1  crate2 ...
LOCK="$1"; shift
for crate in "$@"; do
  grep -q "^name = \"${crate}\"" "$LOCK" && echo "HIT: $crate"
done
```

### Step 3: If You Have Hits

1. **Revoke every credential reachable** from any machine that compiled the malicious
   crate. `build.rs` scripts run at compile time with full system access.
   Cover: crates.io tokens, GitHub tokens (`~/.config/gh/`), SSH keys (`~/.ssh/`), cloud
   creds (`~/.aws/credentials`, `~/.config/gcloud/`), and any env-var-stored API keys.
2. **Remove the dependency** from `Cargo.toml`, regenerate `Cargo.lock`, and commit.
3. **Inspect environment variables and config files** for signs of exfiltration.
   The `mysten-metrics` attack used `build.rs` to run `env`, `cat`, and `ls -R` and POST
   results to a remote server.

## Keeping A Supply Chain Audit Log

Follow the same audit-log discipline described in
[hardening-npm.md](hardening-npm.md#keeping-a-supply-chain-audit-log).
Start from the [template](../supply-chain-audit-log-template.md) in this repository.

## CI Enforcement

CI environments do not source user shell init.
Pass `--locked` explicitly and run scanners as separate steps.

### GitHub Actions

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cargo build --locked
      - run: cargo install --locked cargo-audit
      - run: cargo audit
      - run: cargo install --locked cargo-deny
      - run: cargo deny check
```

### GitLab CI

```yaml
build:
  script:
    - cargo build --locked
    - cargo install --locked cargo-audit && cargo audit
    - cargo install --locked cargo-deny && cargo deny check
```

## Subscribe-And-Watch Feeds

For early warning of new named attacks:

- [RustSec Advisory Database](https://rustsec.org/)
- [Rust Blog (security advisories)](https://blog.rust-lang.org/)
- [Aikido Intel](https://intel.aikido.dev)
- [Socket.dev](https://socket.dev/)
- [Datadog Security Labs](https://securitylabs.datadoghq.com/)

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
