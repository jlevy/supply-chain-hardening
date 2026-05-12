# Go Supply Chain Hardening

**Last updated:** 2026-05-12

**Author:** Joshua Levy (github.com/jlevy) and LLM assistance

A working guide for locking down the Go module toolchain on developer workstations and
CI runners against supply-chain attacks.
Includes concrete configuration recipes, per-platform and per-shell setup,
indicator-of-compromise (IOC) feeds, and local scanning tools.

The doc has three parts:

1. **Background**: why this matters, how Go’s design reduces the attack surface, and
   what residual risks remain.
2. **Notable Exploits**: the named incidents, with affected modules and dates so you can
   spot-check installed `go.mod` files.
   The canonical cross-ecosystem table is in
   [`compromised-packages.md`](../compromised-packages.md); this section provides
   Go-ecosystem context, not a duplicate.
3. **Best Practices for Hardening**: copy-pasteable configuration for the `go`
   toolchain, broken out by platform and shell.

A self-update section at the end describes when to refresh content and which
authoritative sources to verify against.

## Scope

**In scope:** developer-workstation and CI-runner hardening for Go modules.
Configuration of the `go` toolchain (Go 1.21+, with `go mod tidy -diff` requiring Go
1.23+). IOC feeds and local scanners.
Cross-platform: macOS, Linux, and Windows.

**Out of scope:** private module proxy hosting (Athens, Artifactory Go).
Container image scanning.
SBOM generation for compiled binaries (govulncheck covers the dependency-vuln angle).

* * *

# Part 1: Background

Go modules have been the standard dependency system since Go 1.11 (2018), with module
mode becoming the default in Go 1.16 (2021). Unlike npm or PyPI, Go’s module system was
designed with several supply-chain defenses built into the toolchain itself.
That design means the attack surface is meaningfully smaller, but not zero.

## How Go’s Design Reduces The Attack Surface

Four design properties make Go modules structurally more resistant to supply-chain
attacks than ecosystems like npm or PyPI:

1. **No install-time code execution.** Go modules do not run arbitrary code at fetch,
   install, or build time.
   There is no equivalent of npm’s `postinstall` script or PyPI’s `setup.py`. Malicious
   code in a Go module can only execute when the consuming application is compiled and
   run, or when `go test` is invoked.
   This eliminates the entire class of worm-pattern attacks (Shai-Hulud, TanStack) that
   propagate via install hooks.
   ([Go blog: How Go Mitigates Supply Chain Attacks](https://go.dev/blog/supply-chain))

2. **Mandatory checksums via a public transparency log.** Every publicly-fetched module
   version is verified against `sum.golang.org`, a transparency log run by Google.
   The `go.sum` file records expected hashes; the `go` command refuses to use a module
   whose hash does not match.
   Immutable versions mean a published module version cannot be silently replaced
   (unlike npm, where a tarball can be re-published within 72 hours of initial upload
   under certain conditions).
   ([Proposal: Secure the Public Go Module Ecosystem](https://go.googlesource.com/proposal/+/master/design/25530-sumdb.md))

3. **No separate package registry account.** Go modules are imported by their version
   control URL (typically a GitHub path).
   There is no centralized “Go package registry” with separate credentials to phish.
   Account takeover requires compromising the source repository itself (GitHub, GitLab,
   etc.), not a separate registry login.

4. **Default module proxy with caching.** `proxy.golang.org` serves as a caching proxy,
   providing immutability and availability guarantees.
   Once a version is fetched, it cannot be altered at the source without the checksum
   mismatch being caught.

## What Does Not Eliminate Risk

Despite these strengths, several attack vectors remain:

1. **Typosquats.** Go module paths are case-sensitive, and the module namespace is the
   entire space of GitHub (or other VCS) paths.
   An attacker can register `github.com/boltdb-go/bolt` to impersonate
   `github.com/boltdb/bolt`, or `github.com/qiniiu/qmgo` (extra `i`) to impersonate
   `github.com/qiniu/qmgo`. The Go module proxy will cache and serve both as distinct,
   valid modules.
   ([Socket: Malicious Package Exploits Go Module Proxy Caching](https://socket.dev/blog/malicious-package-exploits-go-module-proxy-caching-for-persistence);
   [GitLab: MongoDB Go Module Supply Chain Attack](https://about.gitlab.com/blog/gitlab-catches-mongodb-go-module-supply-chain-attack/))

2. **Module proxy caching as a persistence mechanism.** Once a malicious module version
   is cached by `proxy.golang.org`, the attacker can rewrite the Git tag to point to
   clean code. Manual inspection of the GitHub repo shows nothing suspicious, but
   `go get` continues to serve the cached malicious version.
   The BoltDB typosquat persisted this way for over three years (November 2021 to
   February 2025).
   ([The Register: Researcher Sniffs Out Three-Year Go Supply Chain Attack](https://www.theregister.com/2025/02/04/golang_supply_chain_attack/);
   [The Hacker News: Malicious Go Package Exploits Module Mirror Caching](https://thehackernews.com/2025/02/malicious-go-package-exploits-module.html))

3. **`replace` directives in `go.mod`.** A `replace` directive can redirect any module
   path to an arbitrary local path or remote repository.
   If a developer clones a third-party project containing a `replace` pointing to an
   attacker-controlled fork, `go build` will fetch and compile the replacement silently.
   Unlike npm’s project-local `.npmrc` (overrideable via env vars), `replace` directives
   are part of the module graph and honored unconditionally.

4. **`GOPRIVATE` and `GONOSUMDB` bypass the checksum database.** Modules matching
   `GOPRIVATE` patterns skip `sum.golang.org` verification entirely.
   Misconfiguring `GOPRIVATE` to include public module paths removes the
   transparency-log guarantee for those paths.
   `GONOSUMDB` provides the same bypass with a different semantic intention.

5. **Checksum database bypass via malicious proxy (CVE-2026-42501).** A flaw in the `go`
   command’s validation allowed a malicious module proxy to serve altered module content
   (including Go toolchains selected via `GOTOOLCHAIN`) while returning empty or
   unrelated checksum responses that the `go` command incorrectly accepted.
   Fixed in Go 1.25.10 and 1.26.3.
   ([golang/go#79070](https://github.com/golang/go/issues/79070))

6. **Case-confusion on case-insensitive filesystems.** Go module paths are
   case-sensitive, but macOS (APFS default) and Windows (NTFS) filesystems are
   case-insensitive. The Go toolchain has mitigations (it detects case-insensitive
   collisions in `go mod vendor`), but historical bugs in this area
   ([golang/go#26208](https://github.com/golang/go/issues/26208),
   [golang/go#38342](https://github.com/golang/go/issues/38342),
   [golang/go#38571](https://github.com/golang/go/issues/38571)) show the boundary is
   non-trivial.

## How Big Is This Problem For Go Modules?

**Named incidents per year.** The number of confirmed malicious Go module incidents is
small in absolute terms.
The research record through May 2026 shows roughly a dozen distinct campaigns across
four years:

- **2021-2025:** the BoltDB typosquat (`github.com/boltdb-go/bolt`), discovered February
  2025 but cached since November 2021 (1 module).
- **2025 Q1:** hypert/layout typosquat campaign (7 modules, January-February 2025;
  [Socket](https://socket.dev/blog/typosquatted-go-packages-deliver-malware-loader)).
- **2025 Q1:** fake `x/crypto` module deploying the Rekoobe backdoor (1 module,
  published February 2025;
  [Socket](https://socket.dev/blog/malicious-go-crypto-module-steals-passwords-and-deploys-rekoobe-backdoor);
  [The Hacker News](https://thehackernews.com/2026/02/malicious-go-crypto-module-steals.html)).
- **2025 Q2:** disk-wiper modules impersonating prototransform, go-mcp, tlsproxy (3
  modules, May 2025;
  [Socket](https://socket.dev/blog/wget-to-wipeout-malicious-go-modules-fetch-destructive-payload);
  [BleepingComputer](https://www.bleepingcomputer.com/news/security/linux-wiper-malware-hidden-in-malicious-go-modules-on-github/)).
- **2025 Q2:** MongoDB qmgo typosquats (2 variants, June 2025;
  [GitLab](https://about.gitlab.com/blog/gitlab-catches-mongodb-go-module-supply-chain-attack/)).
- **2026 Q2:** CVE-2026-42501, a toolchain-level checksum bypass (not a malicious
  package, but a mechanism flaw; fixed May 2026).

By comparison, npm saw hundreds of malicious packages per incident in the 2025-2026 wave
(796 in Shai-Hulud 2.0 alone, 84 versions in TanStack), with named campaigns occurring
monthly to weekly. PyPI has tracked dozens of named typosquat campaigns per year since
2023\. Sonatype’s 2026 report found that over 99% of open source malware in 2025
occurred on npm
([Sonatype 2026 State of the Software Supply Chain](https://www.sonatype.com/state-of-the-software-supply-chain/introduction)).

**Why the number is low.** The absence of install-time code execution is the dominant
factor. Worm-pattern attacks (which account for the majority of npm incidents by package
count) cannot propagate through Go modules because there is no lifecycle hook to
exploit. The mandatory checksum database prevents silent version replacement.
The lack of a separate registry account eliminates credential-phishing attacks against a
registry (the attacker must compromise the source VCS account instead).

**Residual risk.** The attacks that do exist in Go are predominantly typosquats that
rely on developer error at `go get` time, plus the module-proxy caching trick that lets
attackers hide malicious code after initial caching.
These are real but low-volume.
The `replace`-directive vector and `GOPRIVATE` bypass are theoretical concerns with no
named incidents to date.

**Assessment.** Relative to npm, Go modules are a **low priority** for active hardening.
The ecosystem’s design eliminates the highest-impact attack class (install-time worms)
entirely and makes the remaining vectors harder to exploit at scale.
The hardening steps in this guide are still worth applying because they are low-effort
and defend against the typosquat and configuration-error vectors that do produce real
incidents, but the urgency is qualitatively different from the npm or PyPI ecosystems.

* * *

# Part 2: Notable Exploits To Be Aware Of

The canonical cross-ecosystem table of named supply-chain incidents lives in
[`compromised-packages.md`](../compromised-packages.md).
Filter to `Ecosystem = Go` for the rows relevant to this guide.
New rows go there first; this section does not duplicate them.

**Reading the table:** if any module path listed there appears in a `go.mod`, you should
(1) remove it, (2) run `go mod tidy`, (3) rotate every credential reachable from any
machine that built or ran code importing the malicious module, and (4) inspect the
system for persistence mechanisms (backdoors, SSH keys, cron jobs).

**Trend line:** through May 2026, Go module supply-chain attacks are infrequent (roughly
quarterly) and small in scale (1-7 modules per campaign).
The predominant vector is typosquatting, not account takeover or worm propagation.

## BoltDB Typosquat: Mechanism And Indicators (2021-2025)

The BoltDB typosquat is notable for demonstrating how the Go module proxy caching
mechanism can be weaponized for long-term persistence.

**Module path:** `github.com/boltdb-go/bolt` (typosquat of `github.com/boltdb/bolt`).

**Timeline:**

- November 2021: attacker publishes `v1.3.1` to GitHub.
  The Go module proxy fetches and caches it.
- After caching: attacker rewrites the Git tag to point to a clean commit.
  GitHub repo now appears benign.
- January 30, 2025: Socket researchers report the module to GitHub and Google.
- February 2025: module removed from the Go module proxy and added to the Go
  vulnerability database.

**Payload:** remote code execution backdoor with C2 communication.

**Detection:** manual analysis by Socket.
The module proxy continued serving the cached malicious version for over three years
despite the GitHub source appearing clean.

([Socket](https://socket.dev/blog/malicious-package-exploits-go-module-proxy-caching-for-persistence);
[Snyk](https://snyk.io/blog/go-malicious-package-alert/);
[The Register](https://www.theregister.com/2025/02/04/golang_supply_chain_attack/))

## Disk-Wiper Modules (May 2025)

Three modules impersonated legitimate projects and delivered a destructive payload.

**Module paths:**

- `github.com/truthfulpharm/prototransform`
- `github.com/blankloggia/go-mcp`
- `github.com/steelpoor/tlsproxy`

**Payload:** obfuscated shell command that downloads `done.sh`, which executes
`dd if=/dev/zero of=/dev/sda bs=1M conv=fsync`. Targets Linux only; checks the OS before
executing.

**Detection:** Socket’s Threat Research Team.
GitHub removed the modules after notification.

([Socket](https://socket.dev/blog/wget-to-wipeout-malicious-go-modules-fetch-destructive-payload);
[BleepingComputer](https://www.bleepingcomputer.com/news/security/linux-wiper-malware-hidden-in-malicious-go-modules-on-github/);
[The Hacker News](https://thehackernews.com/2025/05/malicious-go-modules-deliver-disk.html))

## Fake `x/crypto` With Rekoobe Backdoor (February 2025, Detected Early 2026)

**Module path:** `github.com/xinfeisoft/crypto` (impersonates `golang.org/x/crypto`).

**Payload:** modified `ssh/terminal/terminal.go` hooks the `ReadPassword()` function to
exfiltrate passwords to an attacker-controlled endpoint, then downloads and executes the
Rekoobe Linux backdoor (associated with APT31). Uses a GitHub Raw URL as a C2 pointer
that redirects to `img.spoolsv.cc`.

**Current status:** the Go module proxy returns a 403 SECURITY ERROR for this module.
Any environment that previously cached or vendored it remains at risk.

([Socket](https://socket.dev/blog/malicious-go-crypto-module-steals-passwords-and-deploys-rekoobe-backdoor);
[The Hacker News](https://thehackernews.com/2026/02/malicious-go-crypto-module-steals.html);
[SC Media](https://www.scworld.com/brief/malicious-go-module-steals-passwords-deploys-rekoobe-backdoor))

## MongoDB qmgo Typosquats (June 2025)

**Module paths:**

- `github.com/qiniiu/qmgo` (extra `i` in username; impersonates `github.com/qiniu/qmgo`)
- `github.com/qiiniu/qmgo` (second variant, published four days after the first was
  removed)

**Payload:** malicious code in the `NewClient` function of `client.go`, executed when a
developer initializes a MongoDB connection.

**Detection:** GitLab’s Package Hunter.
First variant removed within 19 hours of report.

([GitLab](https://about.gitlab.com/blog/gitlab-catches-mongodb-go-module-supply-chain-attack/))

## Hypert/Layout Typosquat Campaign (January-February 2025)

**Module paths (hypert impersonators):**

- `github.com/shallowmulti/hypert`
- `github.com/shadowybulk/hypert`
- `github.com/belatedplanet/hypert`
- `github.com/thankfulmai/hypert`

**Module paths (layout impersonators):**

- `github.com/vainreboot/layout`
- `github.com/ornatedoctrin/layout`
- `github.com/utilizedsun/layout`

**Target:** impersonate `github.com/areknoster/hypert` and `github.com/loov/layout`.

**Payload:** obfuscated shell command achieving remote code execution.
Identical obfuscation technique and filenames across all seven modules.

([Socket](https://socket.dev/blog/typosquatted-go-packages-deliver-malware-loader);
[The Hacker News](https://thehackernews.com/2025/03/seven-malicious-go-packages-found.html))

* * *

# Part 3: Best Practices For Hardening

## How Go Module Configuration Works

Go module behavior is controlled by environment variables, `go.mod` directives, and
`go.sum` checksums. Unlike npm, there is no layered config-file precedence to worry
about. The relevant environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `GOPROXY` | `https://proxy.golang.org,direct` | Comma-separated list of module proxy URLs. `direct` means fall back to VCS. |
| `GOSUMDB` | `sum.golang.org` | Checksum database for module verification. |
| `GONOSUMDB` | (empty) | Comma-separated glob patterns of modules to skip checksum verification. |
| `GOPRIVATE` | (empty) | Modules matching these patterns skip both the proxy and the checksum database. Sets `GONOSUMDB` and `GONOPROXY` implicitly. |
| `GOFLAGS` | (empty) | Default flags appended to every `go` command. `-mod=readonly` prevents implicit `go.mod`/`go.sum` modification. |

**Operational conclusion:** set `GOPROXY`, `GOSUMDB`, and `GOFLAGS` explicitly in your
shell environment. Do not rely on the defaults being correct in all contexts.
Avoid widening `GOPRIVATE` or `GONOSUMDB` beyond what is strictly necessary for internal
modules.

## The Three-Control Hardening Pattern

Go’s built-in defenses (no install scripts, mandatory checksums) handle most of what the
npm four-control pattern addresses.
The additional hardening controls for Go target configuration errors and
development-time drift.

### Control 1: Explicit Proxy And Checksum Database

```sh
export GOPROXY="https://proxy.golang.org,direct"
export GOSUMDB="sum.golang.org"
export GONOSUMDB=""
```

Stating these explicitly prevents override by project-level environment files, CI
misconfigurations, or `.envrc` files that set `GONOSUMDB=*` or `GOPRIVATE=*` to work
around proxy issues.

### Control 2: Readonly Module Mode

```sh
export GOFLAGS="-mod=readonly"
```

Prevents `go build`, `go test`, `go run`, and `go install` from silently modifying
`go.mod` or `go.sum`. Any dependency change must be an explicit `go get` or
`go mod tidy` invocation.

### Control 3: Checksum Verification And Drift Detection

```sh
go mod verify    # confirms on-disk modules match go.sum
go mod tidy -diff  # shows what go mod tidy would change; non-zero exit if drift exists
```

Run both in CI. `go mod verify` catches tampering in the module cache.
`go mod tidy -diff` (Go 1.23+) catches stale or missing entries in `go.mod` and
`go.sum`.

## Vendor Mode As A Defense

`go mod vendor` copies all dependencies into a `vendor/` directory within the project.
Building with `-mod=vendor` (or `GOFLAGS="-mod=vendor"`) uses only vendored code, with
no network fetches.

**Benefits:**

- Eliminates dependency on `proxy.golang.org` at build time.
- Makes code review of dependencies possible (all source is in the repo).
- Provides hermetic, reproducible builds.

**Caveats:**

- `go mod verify` does not check vendored code, only the module cache.
  Vendored source could be tampered with in a commit without triggering a checksum
  failure.
- Large vendor directories increase repo size and make dependency diffs noisy.

**Recommendation:** vendor mode is appropriate for high-security environments or when
building in air-gapped networks.
For most projects, the default proxy-plus-checksum-DB mode provides sufficient integrity
with less friction.

## Workspace Mode (`go.work`)

Go 1.18+ supports workspace mode via `go.work` files, allowing multiple modules to be
developed together. Workspace mode uses `use` directives (analogous to `replace` in
effect) to redirect module resolution to local directories.

**Security consideration:** a `go.work` file has the same trust implications as a
`replace` directive.
If you clone a repository containing a `go.work` file, the `use` directives control
which local paths supply module code.
Inspect `go.work` files in third-party repositories before running `go build`.

## The Single Source-Of-Truth Hardening Script

Create one file, `~/.go-hardening.sh`, in POSIX shell syntax.
Source it from every shell init that matters.
The same file works on macOS, Linux, and WSL.

```sh
# ~/.go-hardening.sh — POSIX sh; works in bash, zsh, dash, sh

# Use the default public proxy and checksum database.
# Stating them explicitly prevents accidental override.
export GOPROXY="https://proxy.golang.org,direct"
export GOSUMDB="sum.golang.org"
export GONOSUMDB=""

# Prevent go commands from modifying go.mod and go.sum.
export GOFLAGS="-mod=readonly"
```

## Setup: macOS

### zsh (macOS Default Since 10.15)

```sh
# Append to ~/.zshenv
[ -r "$HOME/.go-hardening.sh" ] && . "$HOME/.go-hardening.sh"
```

### bash (Interactive)

```sh
# Append to ~/.bashrc
[ -r "$HOME/.go-hardening.sh" ] && . "$HOME/.go-hardening.sh"
```

### bash (Login)

macOS Terminal.app opens login shells by default.

```sh
# Append to ~/.bash_profile or ~/.profile
[ -r "$HOME/.go-hardening.sh" ] && . "$HOME/.go-hardening.sh"
```

### fish

```fish
# Append to ~/.config/fish/conf.d/go-hardening.fish
set -gx GOPROXY "https://proxy.golang.org,direct"
set -gx GOSUMDB "sum.golang.org"
set -gx GONOSUMDB ""
set -gx GOFLAGS "-mod=readonly"
```

### Verification (Any Shell On macOS)

```sh
go env GOPROXY      # https://proxy.golang.org,direct
go env GOSUMDB      # sum.golang.org
go env GONOSUMDB # (empty)
go env GOFLAGS      # -mod=readonly
```

## Setup: Linux (Debian/Ubuntu/Fedora/RHEL/Arch)

### bash (Interactive, Non-Login)

```sh
# Append to ~/.bashrc
[ -r "$HOME/.go-hardening.sh" ] && . "$HOME/.go-hardening.sh"
```

### bash (Login)

```sh
# Append to ~/.bash_profile or ~/.profile
[ -r "$HOME/.go-hardening.sh" ] && . "$HOME/.go-hardening.sh"
```

### zsh

```sh
# Append to ~/.zshenv
[ -r "$HOME/.go-hardening.sh" ] && . "$HOME/.go-hardening.sh"
```

### fish

Same recipe as macOS fish above.

### systemd User Environment (Linux-Specific)

```ini
# ~/.config/environment.d/go-hardening.conf
GOPROXY=https://proxy.golang.org,direct
GOSUMDB=sum.golang.org
GONOSUMDB=
GOFLAGS=-mod=readonly
```

## Setup: Windows

### PowerShell 7 (pwsh)

```powershell
# Append to $PROFILE
$env:GOPROXY = "https://proxy.golang.org,direct"
$env:GOSUMDB = "sum.golang.org"
$env:GONOSUMDB = ""
$env:GOFLAGS = "-mod=readonly"
```

### Persistent User-Wide (Survives Reboot)

```powershell
[Environment]::SetEnvironmentVariable("GOPROXY", "https://proxy.golang.org,direct", "User")
[Environment]::SetEnvironmentVariable("GOSUMDB", "sum.golang.org", "User")
[Environment]::SetEnvironmentVariable("GONOSUMDB", "", "User")
[Environment]::SetEnvironmentVariable("GOFLAGS", "-mod=readonly", "User")
```

### Git Bash

```sh
[ -r "$HOME/.go-hardening.sh" ] && . "$HOME/.go-hardening.sh"
```

### WSL

WSL behaves like Linux.
Follow the Linux recipes above.

## Setup: CI Runners

CI environments do not source user shell init.
Inject the variables into the runner’s environment explicitly.

### GitHub Actions

```yaml
env:
  GOPROXY: "https://proxy.golang.org,direct"
  GOSUMDB: "sum.golang.org"
  GONOSUMDB: ""
  GOFLAGS: "-mod=readonly"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
      - run: go mod verify
      - run: go mod tidy -diff
      - run: go build ./...
      - run: go test ./...
      - name: govulncheck
        run: |
          go install golang.org/x/vuln/cmd/govulncheck@latest
          govulncheck ./...
      - name: osv-scanner
        run: |
          osv-scanner scan source --lockfile=go.mod
```

### GitLab CI

```yaml
variables:
  GOPROXY: "https://proxy.golang.org,direct"
  GOSUMDB: "sum.golang.org"
  GONOSUMDB: ""
  GOFLAGS: "-mod=readonly"

stages:
  - build

build:
  stage: build
  image: golang:1.24
  script:
    - go mod verify
    - go mod tidy -diff
    - go build ./...
    - go test ./...
    - go install golang.org/x/vuln/cmd/govulncheck@latest && govulncheck ./...
```

## IOC Feeds

### Tier 1: Free, Machine-Readable, Comprehensive

| Feed | Coverage | How To Consume | Update Lag |
| --- | --- | --- | --- |
| **Go Vulnerability Database** | Official, curated by the Go security team. Includes malicious modules. | Web: `pkg.go.dev/vuln/`; API: `vuln.go.dev/` | Hours after verification |
| **OSV.dev** | All ecosystems including Go; malicious packages tagged with `MAL-*` IDs | REST: `POST https://api.osv.dev/v1/query`; `osv-scanner scan source --lockfile=go.mod` | Minutes after upstream advisory |
| **GitHub Advisory Database (GHSA)** | Go ecosystem advisories | `gh api graphql` for `securityAdvisories`; web filter at `github.com/advisories` | Minutes |
| **deps.dev** (Google) | Dependency graph and vulnerability rollups | REST: `GET https://api.deps.dev/v3/systems/go/packages/<module>` | Same as OSV |

### Tier 2: Free Public Feeds With Attack-Specific Reporting

| Feed | Coverage | How To Consume |
| --- | --- | --- |
| **Socket.dev** | Per-package risk scoring; novel-attack tracking; detected BoltDB, hypert, disk-wiper, and Rekoobe campaigns | Web: `socket.dev`; GitHub App for PRs |
| **Aikido Intel** | Live tracker; affected-module lists | Web: `aikido.dev/intel` |
| **StepSecurity Blog** | CI/CD attack detection | RSS: `stepsecurity.io/blog/feed` |
| **Datadog Security Labs** | Deep technical analysis | Blog: `securitylabs.datadoghq.com` |
| **GitLab Package Hunter** | Detected MongoDB qmgo typosquat | Internal tool; results published on `about.gitlab.com/blog` |

### Tier 3: Commercial

- **Snyk Vulnerability DB**: comprehensive; paid above small-team tier.
- **Phylum**: built around supply-chain-attack detection.
- **JFrog Xray**: fits if already on Artifactory.

## Local Scanning Tools

### `govulncheck` (Official, Go Team)

The recommended baseline scanner.
Call-graph-aware: reports only vulnerabilities in functions your code actually calls,
producing significantly fewer false positives than module-level scanners.

```sh
# Install
go install golang.org/x/vuln/cmd/govulncheck@latest

# Scan the current module
govulncheck ./...

# Scan a specific binary
govulncheck -mode=binary ./path/to/binary

# JSON output for CI integration
govulncheck -format json ./...
```

([Go Vulnerability Management](https://go.dev/doc/security/vuln/);
[govulncheck tutorial](https://go.dev/doc/tutorial/govulncheck))

### `osv-scanner` (Google, Free, Go Binary)

Module-level scan against the OSV database.
Broader ecosystem coverage than govulncheck (covers all OSV sources, not only the Go
vulnerability database).

```sh
# Scan go.mod (V2 syntax; -L go.mod also works)
osv-scanner scan source --lockfile=go.mod

# Recursive scan
osv-scanner scan source -r .
```

### `go mod verify`

Built into the Go toolchain.
Checks that on-disk cached modules match the hashes in `go.sum`. Zero setup.

```sh
go mod verify
```

### `go mod tidy -diff` (Go 1.23+)

Prints what `go mod tidy` would change without modifying files.
Exits non-zero if drift exists.
Ideal for CI gating.

```sh
go mod tidy -diff
```

### deps.dev

Google’s dependency intelligence service.
Provides vulnerability, license, and dependency information for Go modules via a web UI
and REST API.

```
https://deps.dev/go/github.com%2Fsome%2Fmodule
```

## Operational Checklist

### Initial Setup (Every Workstation)

- [ ] Create `~/.go-hardening.sh` (or platform equivalent).
- [ ] Hook it from every shell init that matters.
- [ ] Verify: `go env GOPROXY`, `go env GOSUMDB`, `go env GOFLAGS`.
- [ ] Run `govulncheck ./...` from each workspace root.
- [ ] Run `go mod verify` to confirm module cache integrity.
- [ ] Review `go.mod` for unexpected `replace` directives.
- [ ] Ensure Go is updated to at least 1.25.10 or 1.26.3 (fixes CVE-2026-42501).

### Per-Project (When Adding Or Removing Dependencies)

- [ ] Use `go get <module>@<version>` with an explicit version.
- [ ] Run `go mod tidy` after changes.
- [ ] Run `govulncheck ./...` and `go mod verify`.
- [ ] Review `go.sum` diff for unexpected new modules.
- [ ] Commit `go.mod` and `go.sum` together.

### Weekly

- [ ] Skim the Go Vulnerability Database and OSV.dev for new Go advisories.
- [ ] Run `govulncheck ./...` against active projects.

### When A New Named Attack Drops

- [ ] Grep every `go.mod` in your workspace for the reported module paths.
- [ ] If you have hits: remove the module, run `go mod tidy`, rotate all credentials
  reachable from any machine that built or ran the affected code.
- [ ] Inspect the system for persistence mechanisms specific to the payload (backdoors,
  SSH keys, cron jobs, disk-wipe indicators).

## Common Questions

**Does Go’s lack of install scripts make it immune to supply-chain attacks?** No.
Install-script absence eliminates the worm-class attack vector, but malicious code still
executes when the consuming application is built and run, or when tests are invoked.
A typosquatted module that a developer imports and compiles into their application will
execute its payload at runtime.

**Should I vendor all dependencies?** Vendor mode provides the strongest isolation (no
network fetches at build time, all source reviewable in the repo), but `go mod verify`
does not check vendored code.
If you vendor, treat dependency updates as code reviews.
For most projects, the default proxy-plus-checksum-DB mode is sufficient.

**Is `GOPRIVATE` dangerous?** Only if misconfigured.
`GOPRIVATE` is intended for internal modules hosted on private VCS. Setting
`GOPRIVATE=*` disables the checksum database for all modules, which removes the
transparency-log protection.
Keep `GOPRIVATE` as narrow as possible: list only your organization’s internal module
path prefixes.

**Does `go mod tidy -diff` replace `go mod verify`?** No, they check different things.
`go mod verify` confirms that cached modules match `go.sum` hashes (integrity).
`go mod tidy -diff` checks whether `go.mod` and `go.sum` are complete and minimal
(consistency). Run both.

## Updating This Document

This is a living document.
The threat landscape for Go modules changes on a months-to-quarters cadence; the
hardening controls (env vars, checksum database, scanning tools) change rarely.
Maintain Part 2 (notable exploits) more aggressively than Parts 1 or 3.

Procedures, citation rules, and suggested agent prompts are in
[`self-update-instructions.md`](../self-update-instructions.md) → “Updating Research
Docs”.

* * *

## Sources

### Attack-Specific Writeups (2025-2026)

- [Socket: Malicious Package Exploits Go Module Proxy Caching for Persistence (BoltDB typosquat)](https://socket.dev/blog/malicious-package-exploits-go-module-proxy-caching-for-persistence)
- [Snyk: Do Not Pass Go, Malicious Package Alert (BoltDB)](https://snyk.io/blog/go-malicious-package-alert/)
- [The Register: Researcher Sniffs Out Three-Year Go Supply Chain Attack](https://www.theregister.com/2025/02/04/golang_supply_chain_attack/)
- [The Hacker News: Malicious Go Package Exploits Module Mirror Caching for Persistent Remote Access](https://thehackernews.com/2025/02/malicious-go-package-exploits-module.html)
- [Socket: Typosquatted Go Packages Deliver Malware Loader (hypert/layout)](https://socket.dev/blog/typosquatted-go-packages-deliver-malware-loader)
- [The Hacker News: Seven Malicious Go Packages Found Deploying Malware on Linux and macOS](https://thehackernews.com/2025/03/seven-malicious-go-packages-found.html)
- [Socket: wget to Wipeout, Malicious Go Modules Fetch Destructive Payload (disk-wiper)](https://socket.dev/blog/wget-to-wipeout-malicious-go-modules-fetch-destructive-payload)
- [BleepingComputer: Linux Wiper Malware Hidden in Malicious Go Modules on GitHub](https://www.bleepingcomputer.com/news/security/linux-wiper-malware-hidden-in-malicious-go-modules-on-github/)
- [The Hacker News: Malicious Go Modules Deliver Disk-Wiping Linux Malware](https://thehackernews.com/2025/05/malicious-go-modules-deliver-disk.html)
- [GitLab: GitLab Catches MongoDB Go Module Supply Chain Attack (qmgo)](https://about.gitlab.com/blog/gitlab-catches-mongodb-go-module-supply-chain-attack/)
- [Socket: Malicious Go Crypto Module Steals Passwords and Deploys Rekoobe Backdoor](https://socket.dev/blog/malicious-go-crypto-module-steals-passwords-and-deploys-rekoobe-backdoor)
- [The Hacker News: Malicious Go Crypto Module Steals Passwords, Deploys Rekoobe Backdoor](https://thehackernews.com/2026/02/malicious-go-crypto-module-steals.html)
- [golang/go#79070: CVE-2026-42501, malicious module proxy can bypass checksum database](https://github.com/golang/go/issues/79070)

### Design And Tooling References

- [Go Blog: How Go Mitigates Supply Chain Attacks (Filippo Valsorda, 2022)](https://go.dev/blog/supply-chain)
- [Google Security Blog: Supply Chain Security for Go, Part 1 (2023)](https://security.googleblog.com/2023/04/supply-chain-security-for-go-part-1.html)
- [Go Vulnerability Management](https://go.dev/doc/security/vuln/)
- [govulncheck Tutorial](https://go.dev/doc/tutorial/govulncheck)
- [Go Modules Reference](https://go.dev/ref/mod)
- [Proposal: Secure the Public Go Module Ecosystem (sum.golang.org design)](https://go.googlesource.com/proposal/+/master/design/25530-sumdb.md)
- [OSV.dev, Open Source Vulnerabilities Database](https://osv.dev/)
- [OSV-Scanner on GitHub](https://github.com/google/osv-scanner)
- [deps.dev API](https://deps.dev/)
- [Sonatype 2026 State of the Software Supply Chain](https://www.sonatype.com/state-of-the-software-supply-chain/introduction)

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
