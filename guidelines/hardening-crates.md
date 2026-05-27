# crates.io Operational Hardening

**Last updated:** 2026-05-23

**Author:** Joshua Levy (github.com/jlevy) with agent assistance

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

crates.io has no release-age gate (see the README layered model), so the exception is
about *review*, not bypassing a cool-off.
Verify the crate before you certify or exempt it, and tie the decision to the audit log.

#### Verify First

Confirm the publisher, publish time, and the `.crate` checksum for the exact version:

```sh
cargo info <crate>@<version>     # owners, repository, version metadata (cargo 1.79+)
curl -s https://crates.io/api/v1/crates/<crate>/<version> \
  | jq '.version | {num, created_at, checksum, yanked}'
```

`checksum` is the SHA-256 of the published `.crate` file; `cargo build --locked` records
and re-checks it via `Cargo.lock`. For a crate you maintain, prefer a git dependency
pinned to the reviewed tag so the source stays auditable:

```toml
some-crate = { git = "https://github.com/<org>/<repo>", tag = "v<version>" }
```

#### Then Certify Or Exempt

Two distinct flows; do not mix them:

- **For a crate that you have actually reviewed**, run
  `cargo vet certify <crate> <version>`. Certification is a positive statement ("I read
  this"). Do not certify a crate you have not read; the audit trail becomes worthless.
- **For a crate you need temporarily without reviewing it**, add an exemption in
  `supply-chain/config.toml`. Exemptions are explicit “I am skipping this for now”
  records that other team members can see and chase.

Either way, log the decision in `supply-chain-audit-log.md` per the
[exception process](../README.md#the-exception-process): the reason, the exact
`crate@version`, the verified checksum, and a `Reviewed-by:` sign-off.

### Step 7: Watch `build.rs` And Proc-Macro Crates

Compile-time code execution in Rust comes from two places.
Both run with full filesystem and network access whenever you `cargo build` / `check` /
`test` / `run`.

- **`build.rs`**: package-level build script.
  The `mysten-metrics@9.0.3` attack used `build.rs` to run `env`, `cat`, and `ls -R` and
  POST results to a remote server.
  When adding a dependency, search its source tree for `build.rs` and read it.
- **Proc-macros**: any crate whose `Cargo.toml` declares `proc-macro = true` runs at
  compile time. A proc-macro that does anything besides token-tree manipulation (file
  I/O, network, subprocess) is a red flag.
  Common legitimate examples: `serde_derive`, `tokio-macros`, `proc-macro2` — all
  stable, widely-used, inspected.

`cargo-vet`’s `safe-to-deploy` claims explicitly cover compile-time code; treat unvetted
`build.rs` and proc-macro crates with extra scrutiny.

### Note On `cargo` Aliases

If your shell init sets `alias cargo='cargo --locked'`, that alias protects only
interactive `cargo` invocations.
Scripts, CI runners, `Makefile` rules, and tools that invoke `cargo` directly
(`rust-analyzer`, IDE build, `pre-commit` hooks) do **not** read your shell aliases.
Pass `--locked` explicitly in those contexts, or rely on a committed
`.cargo/config.toml`:

```toml
[build]
# Note: there is no [build] `locked` key. Use environment variables in CI
# (`CARGO_BUILD_LOCKED=true`) or pass `--locked` explicitly. Aliases below help
# interactive shells but are not a security boundary.
```

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

The most relevant crates.io attacks as of 2026-05-23 (no new incidents in May 2026; the
npm/PyPI worms did not reach crates.io).
The cross-ecosystem table is in [`compromised-packages.md`](../compromised-packages.md);
this is the crates.io quick-grep extract:

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

Follow the eight steps in order.
The same outline appears in every per-ecosystem playbook so that incident response stays
consistent regardless of which registry was hit.

1. **Identify scope.** Affected machine(s), exact `cargo build|check|test|run|install`
   command(s), and time window.
   Compile-time payloads (`build.rs`, proc-macros) run on every build, not just install;
   the window is wide.
2. **Preserve evidence before cleanup.** Snapshot the build cache:
   `cp -a ~/.cargo /tmp/audit-snapshot-cargo-$(date +%s)`, save shell history, keep the
   offending `Cargo.lock` and `Cargo.toml`, copy any captured network evidence
   (`dtrace`/`strace` logs if you have them).
3. **Rotate tokens by category.** crates.io tokens (`~/.cargo/credentials.toml`); GitHub
   PAT/OAuth (`~/.config/gh`); SSH (`~/.ssh/*`); cloud (`~/.aws/credentials`,
   `~/.config/gcloud/`); env-var API keys.
   `build.rs` runs at compile time with full filesystem access; assume everything
   readable from the user account is potentially exfiltrated.
4. **Check persistence mechanisms specific to this payload.** The `mysten-metrics@9.0.3`
   build.rs ran `env`/`cat`/`ls -R` and POSTed to a remote server; check outbound DNS
   logs for unexpected hosts.
   The `evm-units` / `uniswap-utils` crates downloaded OS-specific binaries via
   `#[ctor::ctor]`; look for stray binaries in `/tmp`, `~/.cache`, or under
   user-writable PATH entries.
5. **Remove or downgrade the affected dependency.** Remove or pin to a known-good
   version in `Cargo.toml`. If the crate was a transitive dependency, add a
   `[patch.crates-io]` entry or update the direct dependency to one that does not pull
   it.
6. **Regenerate lockfile from trusted sources.** Delete `Cargo.lock`, run
   `cargo generate-lockfile --locked` if possible, or `cargo update` against a trusted
   registry mirror. Commit.
7. **Re-run the scanner to confirm clean.** `cargo audit`, `cargo deny check`, and
   `osv-scanner scan -L Cargo.lock`.
8. **Open a `supply-chain-audit-log.md` entry** using the template (see “Keeping A
   Supply Chain Audit Log” below and
   [`../supply-chain-audit-log-template.md`](../supply-chain-audit-log-template.md)).
   Record raw findings, analysis, every action with timestamps, and any pending
   follow-ups. Redact live credentials per the template’s Redaction Rules.

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
    env:
      CARGO_AUDIT_VERSION: "0.21.2"
      CARGO_DENY_VERSION: "0.16.4"
    steps:
      - uses: actions/checkout@v4
      - run: cargo build --locked
      - run: cargo test --locked
      - run: cargo install --locked --version "$CARGO_AUDIT_VERSION" cargo-audit
      - run: cargo audit
      - run: cargo install --locked --version "$CARGO_DENY_VERSION" cargo-deny
      - run: cargo deny check
```

### GitLab CI

```yaml
build:
  variables:
    CARGO_AUDIT_VERSION: "0.21.2"
    CARGO_DENY_VERSION: "0.16.4"
  script:
    - cargo build --locked
    - cargo test --locked
    - cargo install --locked --version "$CARGO_AUDIT_VERSION" cargo-audit && cargo audit
    - cargo install --locked --version "$CARGO_DENY_VERSION" cargo-deny && cargo deny check
```

**Note on scanner pinning.** The above is the “quick recipe” that fetches scanners from
crates.io at job start.
For production CI, pre-install pinned scanner versions into a hardened runner image (or
cache them by checksum).
Pulling a scanner from `@latest` at every CI run reintroduces a small supply-chain risk
in the audit pipeline itself.

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
