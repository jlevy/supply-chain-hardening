# Crates.io Supply Chain Hardening

**Last updated:** 2026-05-23

**Author:** Joshua Levy (github.com/jlevy) with agent assistance

A working guide for locking down `cargo` on developer workstations and CI runners
against supply-chain attacks targeting the Rust ecosystem.
Includes concrete configuration recipes, per-platform setup, scanning tools, and
indicator-of-compromise (IOC) feeds.

The doc has three parts:

1. **Background**: why this matters, what design properties help or hurt, and how big
   the problem is relative to npm and PyPI.
2. **Notable Exploits**: the named incidents, with affected crates and dates so you can
   spot-check `Cargo.lock` files.
3. **Best Practices for Hardening**: copy-pasteable configuration for `cargo`,
   `cargo-audit`, `cargo-deny`, `cargo-vet`, and CI pipelines.

* * *

# Part 1: Background

The Rust ecosystem uses a single canonical package registry, crates.io, and a single
canonical build tool, `cargo`. Compared to npm (five competing package managers, mutable
versions until recently, install-time script execution by default) or PyPI (pip, uv,
poetry, pdm, setup.py arbitrary code execution), crates.io has several structural
advantages that reduce supply-chain attack surface.
It also has one significant gap: `build.rs` scripts run arbitrary code at compile time.

## How Big Is This Problem For crates.io?

### Named Incidents Per Year

The data is clear: crates.io sees orders of magnitude fewer malicious-package incidents
than npm or PyPI.

- **npm:** Sonatype’s 2026 State of the Software Supply Chain report identified over
  454,600 new malicious packages across all ecosystems in 2025, with npm accounting for
  the vast majority. Snyk flagged over 3,000 malicious npm packages in 2024 alone
  ([Snyk, 2025](https://snyk.io/blog/malicious-packages-open-source-ecosystems/)). Named
  high-impact npm incidents in the 2025-2026 window include qix, Shai-Hulud 1.0,
  Shai-Hulud 2.0, Axios, SAP, TanStack, and several others.
- **PyPI:** Snyk flagged over 600 malicious PyPI packages in 2024
  ([Snyk, 2025](https://snyk.io/blog/malicious-packages-open-source-ecosystems/)). Named
  incidents include the PyTorch `torchtriton` dependency confusion (2022), the
  Ultralytics compromise (2024), and TanStack cross-ecosystem propagation to `mistralai`
  and `guardrails-ai` (2026).
- **crates.io:** The RustSec Advisory Database and Rust Blog document single-digit
  confirmed malicious crate removals per year in 2022-2024, rising to ~15 in 2025 and
  32+ in the first five months of 2026. Named incidents: `rustdecimal` typosquat (2022),
  `faster_log` / `async_println` crypto-key theft (2025), `evm-units` / `uniswap-utils`
  Web3 targeting (2025), `finch-rst` / `sha-rst` credential theft (2025), the
  time-utility campaign (2026), and `mysten-metrics` build.rs exfiltration (2026).
  Download counts for individual malicious crates range from 22 (`sha-rst`) to ~7,400
  (`uniswap-utils`).

### Design Properties That Reduce Attack Surface

1. **Immutable versions.** Once a crate version is published to crates.io, its contents
   cannot be modified. A version can be yanked (hidden from new resolution) but never
   overwritten. This prevents the “publish, wait, replace with malware” pattern.
2. **Mandatory SHA-256 checksums.** The crates.io index stores a SHA-256 checksum for
   every published version.
   Cargo verifies the checksum on download.
   Tampering with a published tarball is detectable.
3. **No install-time script execution by default.** Unlike npm’s `postinstall` or PyPI’s
   `setup.py`, adding a crate to `Cargo.toml` and running `cargo build` does not execute
   arbitrary code at install time (but see `build.rs` below).
4. **Single canonical registry.** The ecosystem defaults to crates.io with no
   second-class public registry that could be confused with it.
   Alternative registries require explicit `[registries]` configuration in
   `.cargo/config.toml`.
5. **`Cargo.lock` pins exact versions by default.** When `Cargo.lock` exists and
   `--locked` is passed, Cargo will not re-resolve dependencies.
   This removes the transitive-upgrade vector that affects npm `install` and pip
   `install`.

### Design Properties That Do Not Reduce Attack Surface

1. **`build.rs` runs arbitrary code at compile time.** This is the Rust equivalent of
   npm’s `postinstall`. Any crate with a `build.rs` script executes that script as part
   of `cargo build`, with full access to the filesystem, network, and environment
   variables. The `mysten-metrics` incident (RUSTSEC-2026-0107) demonstrated exploitation
   of this vector: the `build.rs` ran `env`, `cat`, and `ls -R`, then exfiltrated the
   output via HTTP
   ([GHSA-G38R-8GMR-GHRF](https://github.com/advisories/GHSA-G38R-8GMR-GHRF);
   [DailyCVE](https://dailycve.com/cratesio-malicious-code-rustsec-2026-0107-critical/)).
   Procedural macros (`proc-macro` crates) also execute at compile time with similar
   privileges.
2. **Transitive dependency trees are deep.** A typical Rust project pulls in dozens to
   hundreds of transitive dependencies.
   Each is a trust boundary.
   The `evm-units` attack used `uniswap-utils` as a facade crate that depended on the
   malicious `evm-units`, so users who trusted the facade transitively trusted the
   payload
   ([Rust Blog, 2025-12-03](https://blog.rust-lang.org/2025/12/03/crates.io-malicious-crates-evm-units-and-uniswap-utils/);
   [Socket](https://socket.dev/blog/malicious-rust-crate-evm-units-serves-cross-platform-payloads)).
3. **Cargo trusts crates.io’s name resolution.** There is no built-in mechanism to
   verify that the person publishing `serde_derive` today is the same person who
   published it last year, beyond crates.io’s account system.
   The September 2025 phishing campaign against crates.io users
   ([Rust Blog, 2025-09-12](https://blog.rust-lang.org/2025/09/12/crates-io-phishing-campaign/);
   [Socket](https://socket.dev/blog/crates-io-users-targeted-by-phishing-emails))
   demonstrated that account takeover remains a viable path.
4. **`cargo install` re-resolves by default.** Without `--locked`, `cargo install`
   ignores the packaged `Cargo.lock` and resolves fresh versions from the registry,
   identical to the npm `install` footgun.

### Assessment

crates.io is a **low-to-medium** priority for active hardening relative to npm, and
roughly comparable to PyPI. The structural advantages (immutable versions, mandatory
checksums, no default install-time scripts, single registry) mean the ecosystem is
meaningfully harder to attack at scale.
Confirmed malicious crate incidents numbered in the single digits per year through 2024,
rising to ~15 in 2025 and accelerating in 2026, compared to thousands for npm.
However, `build.rs` provides a compile-time code execution vector that has been
exploited in practice (RUSTSEC-2026-0107), and the September 2025 phishing campaign
shows that account-takeover attacks are being attempted against Rust maintainers.
The hardening steps in Part 3 are straightforward and worth applying, even though the
threat volume is far lower than in the npm ecosystem.

## What The Attacks Have In Common

Across the confirmed crates.io incidents, the pattern is narrower than in npm:

1. **Typosquatting or name confusion.** `rustdecimal` vs `rust_decimal`, `faster_log` vs
   `fast_log`, `finch-rst` vs `finch`. The attacker publishes a crate with a name close
   to a popular one and waits for typos.
2. **Credential or key theft.** Most payloads target cryptocurrency private keys
   (`faster_log`, `evm-units`), environment variables and CI secrets (`mysten-metrics`,
   time-utility campaign), or crates.io/GitHub tokens (`finch-rst`).
3. **Low download counts.** Unlike npm, where worm-class attacks achieve millions of
   installs via high-download libraries, crates.io incidents typically accumulate
   hundreds to low thousands of downloads before detection.

* * *

# Part 2: Notable Exploits To Be Aware Of

The canonical cross-ecosystem table of named supply-chain incidents lives in
[`compromised-packages.md`](../compromised-packages.md).
Filter to `Ecosystem = crates.io` for the rows relevant to this guide.
New rows go there first; this section does not duplicate them.

**Reading the table:** if any crate listed there appears in a `Cargo.lock`, you should
(1) rotate every credential reachable from any machine that compiled the affected crate,
and (2) remove the dependency, regenerate `Cargo.lock`, and rebuild.

**Trend line:** through May 2026, crates.io incidents appear at a pace of roughly one
named campaign every 2-3 months, compared to weekly-to-monthly for npm.
A May 2026 review of the RustSec advisory database and the incident feeds found **no new
malicious-crate incidents** in that month, and confirmed that the npm/PyPI worm
campaigns (Shai-Hulud, Mini Shai-Hulud, TeamPCP) did not propagate to crates.io.
The most recent crates.io incident remains `mysten-metrics@9.0.3` (build.rs
exfiltration, April 2026). The dominant crates.io vector stays runtime/build-time
payloads in typosquats (`build.rs`, proc-macros, `#[ctor]`), which a release-age delay
does not address; the `--locked` + `cargo audit`/`deny`/`vet` controls in Part 3 remain
the right defense.

## Incident Summaries

### `rustdecimal` Typosquat (2022-05)

**Advisory:** RUSTSEC-2022-0042, GHSA-7pwq-f4pq-78gm.

Typosquat of the legitimate `rust_decimal` crate.
The malicious `rustdecimal@1.23.1` contained identical source code except for the
`Decimal::new` function, which checked for the `GITLAB_CI` environment variable and, if
present, downloaded and executed a second-stage payload.
The malware targeted both Linux and macOS. The crate had fewer than 500 downloads and no
reverse dependencies on crates.io.
Removed 2022-05-02.

Sources:
[Rust Blog, 2022-05-10](https://blog.rust-lang.org/2022/05/10/malicious-crate-rustdecimal/);
[RustSec](https://rustsec.org/advisories/RUSTSEC-2022-0042.html);
[GHSA-7pwq-f4pq-78gm](https://github.com/advisories/GHSA-7pwq-f4pq-78gm);
[Sonatype](https://www.sonatype.com/blog/this-week-in-malware-may-13th-edition).

### `faster_log` And `async_println` Crypto-Key Theft (2025-09)

Typosquat of the legitimate `fast_log` crate.
Published 2025-05-25 by users `rustguruman` and `dumbnbased`, with 8,424 combined
downloads. Both crates copied legitimate source code and added routines that scanned
local Rust source files for Solana and Ethereum private keys, then exfiltrated matches
via HTTP POST to a hardcoded Cloudflare Workers endpoint.
The malicious code executed at runtime, not at build time.
Removed 2025-09-24.

Sources:
[Rust Blog, 2025-09-24](https://blog.rust-lang.org/2025/09/24/crates.io-malicious-crates-fasterlog-and-asyncprintln/);
[Socket](https://socket.dev/blog/two-malicious-rust-crates-impersonate-popular-logger-to-steal-wallet-keys);
[The Hacker News, 2025-09-25](https://thehackernews.com/2025/09/malicious-rust-crates-steal-solana-and.html).

### crates.io Phishing Campaign (2025-09)

Not a malicious crate, but a credential-theft campaign targeting crate publishers.
Emails from `rustfoundation.dev` (not controlled by the Rust Foundation) impersonated
breach notifications and directed recipients to a fake GitHub login page at
`github.rustfoundation.dev`. Emails arrived minutes after a developer published a new
crate, indicating the attacker monitored the crates.io publish feed in real time.

Sources:
[Rust Blog, 2025-09-12](https://blog.rust-lang.org/2025/09/12/crates-io-phishing-campaign/);
[Socket](https://socket.dev/blog/crates-io-users-targeted-by-phishing-emails);
[Help Net Security, 2025-09-15](https://www.helpnetsecurity.com/2025/09/15/phishing-campaign-targets-rust-developers/).

### `evm-units` And `uniswap-utils` Web3 Targeting (2025-12)

Published by user `ablerust` in April 2025, removed December 2025. `evm-units` had over
7,000 downloads; `uniswap-utils` had 14 versions and over 7,400 downloads.
`uniswap-utils` depended on `evm-units`, forming a transitive-trust chain.
The payload detected the OS and presence of Qihoo 360 antivirus, then downloaded and
executed a binary from a remote server.
Targeted Web3 developers in Asian markets.

Sources:
[Rust Blog, 2025-12-03](https://blog.rust-lang.org/2025/12/03/crates.io-malicious-crates-evm-units-and-uniswap-utils/);
[Socket](https://socket.dev/blog/malicious-rust-crate-evm-units-serves-cross-platform-payloads);
[The Hacker News, 2025-12-04](https://thehackernews.com/2025/12/malicious-rust-crate-delivers-os.html).

### `finch-rst` And `sha-rst` Credential Theft (2025-12)

Typosquats of the `finch` and `finch_cli` crates.
`sha-rst` was a dependency of `finch_cli_rust` and `finch-rst`, containing the
exfiltration payload.
Published 2025-12-08, with 22 downloads for `sha-rst` and 21 for `finch-rst`. Reported
by Matthias Zepper of National Genomics Infrastructure Sweden.
Removed 2025-12-08.

Note: the Rust Blog post of 2025-12-05 covers a related but distinct pair (`finch-rust`
and `sha-rust`, RUSTSEC-2025-0148 and RUSTSEC-2025-0146) published earlier in November
2025 and reported by Socket.

Sources:
[RustSec RUSTSEC-2025-0150](https://rustsec.org/advisories/RUSTSEC-2025-0150.html);
[RustSec RUSTSEC-2025-0151](https://rustsec.org/advisories/RUSTSEC-2025-0151.html);
[RustSec RUSTSEC-2025-0152](https://rustsec.org/advisories/RUSTSEC-2025-0152.html).

### Time-Utility Campaign (2026-02/03)

Five crates published between late February and early March 2026: `chrono_anchor`,
`dnp3times`, `time_calibrator`, `time_calibrators`, and `time-sync`. All impersonated
time-related utilities and exfiltrated `.env` files.
`chrono_anchor` used obfuscation techniques to avoid detection.

Sources:
[Socket](https://socket.dev/blog/5-malicious-rust-crates-posed-as-time-utilities-to-exfiltrate-env-files);
[The Hacker News, 2026-03-11](https://thehackernews.com/2026/03/five-malicious-rust-crates-and-ai-bot.html).

### `mysten-metrics` build.rs Exfiltration (2026-04)

**Advisory:** RUSTSEC-2026-0107, GHSA-G38R-8GMR-GHRF.

Impersonation of Mysten Labs infrastructure.
`mysten-metrics@9.0.3` contained a malicious `build.rs` that ran `env`, `cat`, and
`ls -R` at compile time, then exfiltrated the output via HTTP POST. This is the clearest
documented example of `build.rs` as a supply-chain attack vector on crates.io.
Reported 2026-04-20, removed 2026-04-22.

Sources: [GHSA-G38R-8GMR-GHRF](https://github.com/advisories/GHSA-G38R-8GMR-GHRF);
[DailyCVE](https://dailycve.com/cratesio-malicious-code-rustsec-2026-0107-critical/).

* * *

# Part 3: Best Practices For Hardening

## How Cargo Dependency Resolution Works

Cargo resolves dependencies by reading `Cargo.toml`, consulting the crates.io index (a
Git or sparse-protocol repository of crate metadata and SHA-256 checksums), downloading
tarballs, and verifying checksums against the index.

The critical precedence:

```
HIGHEST PRIORITY  ->  --locked (use Cargo.lock exactly as committed)
                  ->  Cargo.lock (pin resolved versions)
                  ->  Cargo.toml version requirements (semver ranges)
LOWEST PRIORITY   ->  crates.io index (latest compatible version)
```

Without `--locked`, Cargo may re-resolve to newer versions within the semver range
specified in `Cargo.toml`. With `--locked`, Cargo refuses to build if the resolved graph
does not exactly match `Cargo.lock`.

**Operational conclusion:** always pass `--locked` for builds where reproducibility and
safety matter (CI, deployments, `cargo install`).

## The Three-Control Hardening Pattern

### Control 1: `--locked` (Lockfile Enforcement)

Pass `--locked` to `cargo build`, `cargo run`, `cargo test`, and `cargo install`.

- **Catches:** transitive dependency re-resolution to a newly published malicious
  version.
- **Bypass per command:** omit `--locked` when intentionally updating dependencies, then
  review and commit the updated `Cargo.lock`.

### Control 2: `cargo-audit` (Known-Vulnerability Scanning)

`cargo-audit` checks your `Cargo.lock` against the RustSec Advisory Database.

```sh
cargo install --locked cargo-audit
cargo audit
```

- **Catches:** any crate version with a published RustSec advisory, including malicious
  crates (categorized as `"malicious"` in the advisory’s `categories` field).
- **Limitation:** reactive, not preventive.
  The advisory must exist before `cargo audit` flags it.

### Control 3: `cargo-deny` (Policy-As-Code)

`cargo-deny` enforces configurable policies: banned crate versions, license family
restrictions, duplicate transitive dependency detection, and allowed registry sources.

```sh
cargo install --locked cargo-deny
cargo deny init    # generates deny.toml
cargo deny check
```

Example `deny.toml` entries:

```toml
[bans]
# Ban specific crate versions known to be malicious
deny = [
    { name = "rustdecimal" },
    { name = "faster_log" },
    { name = "async_println" },
    { name = "evm-units" },
    { name = "mysten-metrics" },
]

[sources]
# Only allow crates from crates.io (block alternative registries and git sources)
unknown-registry = "deny"
unknown-git = "deny"
allow-registry = ["https://github.com/rust-lang/crates.io-index"]
allow-git = []
```

- **Catches:** banned crates, unauthorized registries, license violations, duplicate
  transitive deps.
- **Bypass:** explicitly allow in `deny.toml` with a comment explaining why.

## Additional Tools

### `cargo-vet` (Mozilla, Audit Management)

`cargo-vet` records audit entries certifying that a specific crate version has been
reviewed by a trusted auditor.
Teams share audit logs so each crate is reviewed once.

```sh
cargo install --locked cargo-vet
cargo vet init
cargo vet
```

Organizations import each other’s audit results:

```sh
cargo vet import mozilla https://raw.githubusercontent.com/nickel-org/nickel.rs/main/supply-chain/audits.toml
```

Strongest option for teams with a formal review process.

### `cargo-crev` (Community Web-Of-Trust)

An alternative to `cargo-vet` using a decentralized web-of-trust model.
Reviewers publish signed reviews to public Git repositories, and you configure a trust
graph of reviewers whose judgment you accept.

```sh
cargo install --locked cargo-crev
cargo crev id new
cargo crev crate verify
```

`cargo-crev` has broader community adoption among individual Rust developers.
`cargo-vet` is more commonly used in organizational settings (Mozilla, Google).
Both serve the same purpose: ensuring a human has looked at the code.

### `osv-scanner` (Google, Cross-Ecosystem)

Scans `Cargo.lock` against the OSV database, which aggregates RustSec, GHSA, and other
sources. Useful if you also scan npm, PyPI, or Go lockfiles in the same CI pipeline.

```sh
osv-scanner scan -L Cargo.lock
```

## Setup: macOS, Linux, And Windows

Cargo is cross-platform and the hardening commands are identical across macOS, Linux,
and Windows. The only variation is shell init for environment-level configuration.

### Shell Alias (All Platforms)

Add to your shell init (`~/.bashrc`, `~/.zshenv`, or PowerShell `$PROFILE`):

```sh
alias cargo-build='cargo build --locked'
alias cargo-install='cargo install --locked'
alias cargo-run='cargo run --locked'
```

There is no `config.toml` setting to make `cargo build` default to `--locked`; pass it
explicitly or use the alias.
`cargo install` also requires `--locked` on every invocation (there is no global config
equivalent).

### PowerShell

```powershell
# Append to $PROFILE
function cargo-build { cargo build --locked @args }
function cargo-install { cargo install --locked @args }
Set-Alias cb cargo-build
Set-Alias ci cargo-install
```

## Setup: CI Runners

### GitHub Actions

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable

      - name: Build (locked)
        run: cargo build --locked

      - name: Audit (RustSec)
        run: |
          cargo install --locked cargo-audit
          cargo audit

      - name: Deny check (policy)
        run: |
          cargo install --locked cargo-deny
          cargo deny check

      - name: OSV scan
        run: |
          curl -sSfL https://github.com/google/osv-scanner/releases/latest/download/osv-scanner_linux_amd64 -o osv-scanner
          chmod +x osv-scanner
          ./osv-scanner scan -L Cargo.lock
```

### GitLab CI

```yaml
build:
  image: rust:latest
  script:
    - cargo build --locked
    - cargo install --locked cargo-audit && cargo audit
    - cargo install --locked cargo-deny && cargo deny check
```

## `build.rs` Risk Mitigation

`build.rs` is the primary code-execution vector in the Rust supply chain.
Mitigations:

1. **Review `build.rs` of new dependencies.** Before adding a crate, check whether it
   has a `build.rs` and what it does.
   `cargo-vet` and `cargo-crev` formalize this review.
2. **Sandbox builds.** Run `cargo build` inside containers or VMs for untrusted
   dependency trees. CI runners are ephemeral by default, which limits persistence but
   not exfiltration.
3. **Monitor network egress.** A `build.rs` that makes HTTP requests during compilation
   is suspicious. Network monitoring or firewall rules on build machines can detect this.
4. **Use `cargo-deny` to restrict sources.** Setting `unknown-registry = "deny"` and
   `unknown-git = "deny"` in `deny.toml` ensures all dependencies come from crates.io.

## Alternative Registries

Cargo supports alternative registries via `.cargo/config.toml`:

```toml
[registries]
my-company = { index = "sparse+https://my-registry.example.com/index/" }
```

Security considerations:

- A project-local `.cargo/config.toml` can redirect dependency resolution to a
  non-crates.io registry.
  Cloning an untrusted repository and running `cargo build` could pull crates from an
  attacker-controlled server.
- Use `cargo-deny` source restrictions to enforce that only crates.io (and explicitly
  approved private registries) are allowed.
- Credentials for alternative registries go in `.cargo/credentials.toml`, not
  `.cargo/config.toml`, to keep secrets out of version control.

## `cargo install` Vs Project Dependencies

These are different attack surfaces:

- **Project dependencies** (`Cargo.toml` + `Cargo.lock`): pinned by the lockfile.
  Pass `--locked` and the resolved tree does not change.
- **`cargo install`**: by default, ignores the packaged `Cargo.lock` and re-resolves
  from scratch. A malicious version published since the tool author last updated could be
  pulled in. Always use `cargo install --locked`.

## IOC Feeds

### Tier 1: Free, Machine-Readable

| Feed | Coverage | How To Consume |
| --- | --- | --- |
| **RustSec Advisory DB** | Rust crates only; includes malware advisories | `cargo audit`; raw Git at `github.com/rustsec/advisory-db` |
| **OSV.dev** | All ecosystems; `MAL-*` IDs for malicious packages | REST: `POST https://api.osv.dev/v1/query`; `osv-scanner scan -L Cargo.lock` |
| **GHSA** | GitHub advisories; filter to crates.io ecosystem | `gh api graphql` for `securityAdvisories` |

### Tier 2: Free Public Feeds With Attack-Specific Reporting

| Feed | Coverage | How To Consume |
| --- | --- | --- |
| **Rust Blog** | Official security advisories for crates.io incidents | RSS at `blog.rust-lang.org/feed.xml` |
| **Socket.dev** | Per-package risk scoring; sandboxed execution | Web UI plus CLI |
| **Aikido Intel** | Cross-ecosystem live tracker | Web at `aikido.dev/intel` |
| **Datadog Security Labs** | Technical analysis of supply-chain attacks | Blog: `securitylabs.datadoghq.com` |

### Tier 3: Commercial

- **Snyk Vulnerability DB**: comprehensive; paid above small-team tier.
- **Phylum**: supply-chain-attack focused.
- **ReversingLabs**: open-source malware detection across registries.

## Operational Checklist

### Initial Setup (Every Workstation)

- [ ] Install `cargo-audit` and `cargo-deny` (`cargo install --locked`).
- [ ] Create `deny.toml` in each project (`cargo deny init`).
- [ ] Add shell aliases so `cargo build`, `cargo install`, and `cargo run` always pass
  `--locked` (see “Shell Alias” above).
- [ ] Run `cargo audit` in each workspace; investigate any hits.
- [ ] Optionally install `cargo-vet` or `cargo-crev` for human-review attestations.

### Per-Project (When Adding Or Removing Dependencies)

- [ ] After adding a crate, review whether it has a `build.rs` or is a `proc-macro`.
  Check what it does.
- [ ] Run `cargo audit` and `cargo deny check`.
- [ ] Commit `Cargo.lock`.
- [ ] If using `cargo-vet`, run `cargo vet` and certify or exempt the new crate.

### Weekly

- [ ] Skim RustSec advisories and Rust Blog for new malicious-crate announcements.
- [ ] Run `cargo audit` in each workspace to pick up newly published advisories.

### When A New Named Attack Drops

- [ ] Grep `Cargo.lock` for the affected crate names.
- [ ] If you have hits: revoke every credential reachable from any machine that compiled
  the crate. Rotate crates.io tokens, GitHub tokens, SSH keys, cloud credentials.
- [ ] Remove the dependency, regenerate `Cargo.lock`, rebuild.
- [ ] Open an audit-log entry per
  [hardening-npm.md](../guidelines/hardening-npm.md#keeping-a-supply-chain-audit-log).

## Updating This Document

This is a living document.
The threat landscape for crates.io changes on a months-to-quarters cadence.
Maintain Part 2 (notable exploits) more aggressively than Parts 1 or 3.

Procedures, citation rules, and suggested agent prompts are in
[`self-update-instructions.md`](../self-update-instructions.md) -> “Updating Research
Docs”.

* * *

## Sources

### Attack-Specific Writeups

- [Rust Blog: Security advisory: malicious crate rustdecimal (2022-05-10)](https://blog.rust-lang.org/2022/05/10/malicious-crate-rustdecimal/)
- [RustSec RUSTSEC-2022-0042](https://rustsec.org/advisories/RUSTSEC-2022-0042.html)
- [GHSA-7pwq-f4pq-78gm: `rustdecimal` is a malicious crate](https://github.com/advisories/GHSA-7pwq-f4pq-78gm)
- [Sonatype: Malicious Rust Crate and Colors Typosquats (2022-05-13)](https://www.sonatype.com/blog/this-week-in-malware-may-13th-edition)
- [Rust Blog: Malicious crates faster_log and async_println (2025-09-24)](https://blog.rust-lang.org/2025/09/24/crates.io-malicious-crates-fasterlog-and-asyncprintln/)
- [Socket: Two Malicious Rust Crates Impersonate Popular Logger to Steal Wallet Keys](https://socket.dev/blog/two-malicious-rust-crates-impersonate-popular-logger-to-steal-wallet-keys)
- [The Hacker News: Malicious Rust Crates Steal Solana and Ethereum Keys (2025-09-25)](https://thehackernews.com/2025/09/malicious-rust-crates-steal-solana-and.html)
- [Rust Blog: crates.io phishing campaign (2025-09-12)](https://blog.rust-lang.org/2025/09/12/crates-io-phishing-campaign/)
- [Socket: Crates.io Users Targeted by Phishing Emails](https://socket.dev/blog/crates-io-users-targeted-by-phishing-emails)
- [Help Net Security: Phishing campaign targets Rust developers (2025-09-15)](https://www.helpnetsecurity.com/2025/09/15/phishing-campaign-targets-rust-developers/)
- [Rust Blog: Malicious crates evm-units and uniswap-utils (2025-12-03)](https://blog.rust-lang.org/2025/12/03/crates.io-malicious-crates-evm-units-and-uniswap-utils/)
- [Socket: Malicious Rust Crate evm-units Serves Cross-Platform Payloads](https://socket.dev/blog/malicious-rust-crate-evm-units-serves-cross-platform-payloads)
- [The Hacker News: Malicious Rust Crate Delivers OS-Specific Malware (2025-12-04)](https://thehackernews.com/2025/12/malicious-rust-crate-delivers-os.html)
- [Rust Blog: Malicious crates finch-rust and sha-rust (2025-12-05)](https://blog.rust-lang.org/2025/12/05/crates.io-malicious-crates-finch-rust-and-sha-rust/)
  (covers the related `finch-rust`/`sha-rust` pair, not the `finch-rst`/`sha-rst` pair)
- [RustSec RUSTSEC-2025-0150: finch-rst](https://rustsec.org/advisories/RUSTSEC-2025-0150.html)
- [RustSec RUSTSEC-2025-0151: sha-rst](https://rustsec.org/advisories/RUSTSEC-2025-0151.html)
- [RustSec RUSTSEC-2025-0152: finch_cli_rust](https://rustsec.org/advisories/RUSTSEC-2025-0152.html)
- [Socket: 5 Malicious Rust Crates Posed as Time Utilities to Exfiltrate .env Files](https://socket.dev/blog/5-malicious-rust-crates-posed-as-time-utilities-to-exfiltrate-env-files)
- [The Hacker News: Five Malicious Rust Crates and AI Bot Exploit CI/CD Pipelines (2026-03-11)](https://thehackernews.com/2026/03/five-malicious-rust-crates-and-ai-bot.html)
- [GHSA-G38R-8GMR-GHRF: mysten-metrics build.rs Malicious Code Execution](https://github.com/advisories/GHSA-G38R-8GMR-GHRF)
- [Rust Blog: Update to malicious crate notification policy (2026-02-13)](https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/)

### Industry Reports

- [Sonatype: 2026 State of the Software Supply Chain](https://www.sonatype.com/state-of-the-software-supply-chain/2026/open-source-malware)
- [ReversingLabs: 2026 Software Supply Chain Security Report](https://www.reversinglabs.com/sscs-report)
- [Snyk: The rising trend of malicious packages in open source ecosystems (2025)](https://snyk.io/blog/malicious-packages-open-source-ecosystems/)

### Tools And Feeds

- [RustSec Advisory Database](https://rustsec.org/)
- [cargo-audit on crates.io](https://crates.io/crates/cargo-audit)
- [cargo-deny on GitHub (Embark Studios)](https://github.com/EmbarkStudios/cargo-deny)
- [cargo-vet on GitHub (Mozilla)](https://github.com/mozilla/cargo-vet)
- [cargo-crev on GitHub](https://github.com/crev-dev/cargo-crev)
- [OSV.dev](https://osv.dev/)
- [OSV-Scanner on GitHub](https://github.com/google/osv-scanner)
- [Cargo Registries documentation](https://doc.rust-lang.org/cargo/reference/registries.html)

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
