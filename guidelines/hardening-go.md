# Go Modules Operational Hardening

**Last updated:** 2026-05-12

**Author:** Joshua Levy (github.com/jlevy) with agent assistance

The minimum action list to harden a workstation or CI runner against Go module
supply-chain attacks, and to check whether you have already been compromised.
Full threat model, incident timeline, and scanning-tool comparisons in
[research-go-supply-chain-hardening.md](../research/research-go-supply-chain-hardening.md).

## Hardening (Ten-Minute Setup)

### Step 0: Keep The Go Toolchain Current

Use Go 1.25.10 or 1.26.3 (or later) to pick up the fix for **CVE-2026-42501**, a
malicious module proxy that could bypass the public checksum database (`sum.golang.org`)
for selected modules and toolchains.
If you used an untrusted `GOPROXY` between the introduction of the affected behaviour
and your upgrade, regenerate `go.sum` from trusted sources and run `go mod verify`
afterward:

```sh
go version                       # confirm >= 1.25.10 or >= 1.26.3
go env -w GOPROXY=https://proxy.golang.org,direct   # default public proxy
go mod tidy                      # regenerate go.sum entries from the trusted proxy
go mod verify                    # checksum check against go.sum
```

For high-security environments that should never auto-download toolchains, also set
`GOTOOLCHAIN=local` (Step 1 below).
That is defense-in-depth; it is **not** a substitute for upgrading to a fixed Go
release.

Full background and the upstream issue: see
[research-go-supply-chain-hardening.md → CVE-2026-42501](../research/research-go-supply-chain-hardening.md#part-1-background).

### Step 1: Create The Hardening Script

Create `~/.go-hardening.sh` with the protection env vars:

```sh
# Use the default public proxy and checksum database.
# Stating them explicitly prevents accidental override by project-level env files.
export GOPROXY="https://proxy.golang.org,direct"
export GOSUMDB="sum.golang.org"
export GONOSUMDB=""

# Prevent go commands from modifying go.mod and go.sum.
export GOFLAGS="-mod=readonly"

# Prevent fetching or building modules not already in the local cache.
# Uncomment for air-gapped or high-security environments:
# export GOFLAGS="-mod=vendor"

# Strict-mode option: refuse automatic toolchain downloads (do not let go.mod's
# `toolchain` directive trigger a download). Defense-in-depth on top of Step 0's
# upgrade. Leave commented unless you have a controlled toolchain distribution.
# export GOTOOLCHAIN=local
```

### Step 2: Source From Shell Init

Pick the line for every shell you use.
Detail on each in
[research-go-supply-chain-hardening.md](../research/research-go-supply-chain-hardening.md#part-3-best-practices-for-hardening).

- **zsh** (any OS): add to `~/.zshenv`
  `[ -r "$HOME/.go-hardening.sh" ] && . "$HOME/.go-hardening.sh"`
- **bash, interactive** (any OS): add the same line to `~/.bashrc`.
- **bash, login** (macOS Terminal default, SSH sessions): add the same line to
  `~/.bash_profile` or `~/.profile`.
- **fish**: add to `~/.config/fish/conf.d/go-hardening.fish`:
  ```fish
  set -gx GOPROXY "https://proxy.golang.org,direct"
  set -gx GOSUMDB "sum.golang.org"
  set -gx GONOSUMDB ""
  set -gx GOFLAGS "-mod=readonly"
  ```
- **Windows PowerShell**: add to `$PROFILE` (see
  [research-go-supply-chain-hardening.md](../research/research-go-supply-chain-hardening.md#powershell-7-pwsh)).

### Step 3: Verify

```sh
# Shell-state check: every variable is set in the current shell.
env | grep -E '^GO(PROXY|SUMDB|NOSUMDB|FLAGS|TOOLCHAIN)='

# Tool view: go reports the values it will actually use (merges shell env with
# Go's persisted config from `go env -w`). If these differ from the shell view
# above, `go env -w` has written a config that overrides your shell init.
go env GOPROXY      # https://proxy.golang.org,direct
go env GOSUMDB      # sum.golang.org
go env GONOSUMDB    # (empty)
go env GOFLAGS      # -mod=readonly
go mod verify       # all modules verified
```

### Step 4: When You Intentionally Modify Dependencies

Unset the readonly flag per command, visibly.
Note: `GOFLAGS=""` clears **all** default Go flags, not only `-mod=readonly`. If you
also set other flags in `GOFLAGS` (e.g. `-tags=...`), use targeted overrides:

```sh
# Cleanest: explicit per-command override of just -mod
go get -mod=mod -u github.com/some/module@v1.2.3
go mod tidy -mod=mod

# If you need to clear GOFLAGS entirely (loses other defaults too):
GOFLAGS="" go get -u github.com/some/module@v1.2.3
```

### Source-Policy Checks

Two patterns in `go.mod` and the workspace warrant routine review:

- **Unexpected `replace` and `exclude` directives.** `replace` can swap a public module
  for a local path or a different fork; that is exactly how an attacker with PR access
  can redirect a sensitive import.
  Grep `go.mod` and `go.work` for `^replace ` and `^exclude ` and verify each entry is
  intentional.
- **Overly broad `GOPRIVATE` / `GONOSUMCHECK` / `GONOSUMDB`.** A wildcard like
  `GOPRIVATE=*` disables checksum-database verification for every module, not just
  internal ones. Always narrow to specific module prefixes (e.g.
  `GOPRIVATE=github.com/your-org/*`). Audit with:

```sh
go env GOPRIVATE GONOSUMCHECK GONOSUMDB
git grep -nE '^(replace|exclude) ' -- '*.mod' '*.work'
```

- **`go.work` files.** A `go.work` file overrides module resolution for a multi-module
  workspace. Verify each `use` entry is a path you control.
  A hostile PR can add a `use ../malicious-fork` directive that hijacks every module
  reference.

## Compromise Assessment

### Step 1: Verify Module Integrity

```sh
# Check that on-disk modules match go.sum checksums.
go mod verify

# Check for drift: would go mod tidy change anything?
# Requires Go 1.23+. Non-zero exit if go.mod or go.sum would change.
go mod tidy -diff
```

### Step 2: Scan For Known Vulnerabilities

```sh
# Install once: go install golang.org/x/vuln/cmd/govulncheck@latest
# Call-graph-aware: reports only reachable vulns.
govulncheck ./...

# Alternative, module-level scan (no call-graph analysis):
# Install once: https://github.com/google/osv-scanner/releases
osv-scanner scan source --lockfile=go.mod
```

### Step 3: Grep For Known IOCs From Recent Named Attacks

The most relevant Go module attacks as of 2026-05-12. The cross-ecosystem table is in
[`compromised-packages.md`](../compromised-packages.md); this is the Go quick-grep
extract:

| Date | Name | Quick IOC Pattern |
| --- | --- | --- |
| 2026-02 | Fake `x/crypto` (Rekoobe) | `github.com/xinfeisoft/crypto` in any `go.mod` or import |
| 2025-05 | Disk-wiper modules | `github.com/truthfulpharm/prototransform`, `github.com/blankloggia/go-mcp`, `github.com/steelpoor/tlsproxy` |
| 2025-06 | MongoDB qmgo typosquat | `github.com/qiniiu/qmgo` or `github.com/qiiniu/qmgo` |
| 2025-01..02 | hypert/layout typosquats | `github.com/shallowmulti/hypert`, `github.com/shadowybulk/hypert`, `github.com/belatedplanet/hypert`, `github.com/thankfulmai/hypert`, `github.com/vainreboot/layout`, `github.com/ornatedoctrin/layout`, `github.com/utilizedsun/layout` |
| 2021-11..2025-02 | BoltDB typosquat | `github.com/boltdb-go/bolt` |

Quick grep template:

```sh
#!/usr/bin/env bash
# Usage: scan-go-iocs.sh /path/to/go.mod  ioc1  ioc2 ...
MOD="$1"; shift
for ioc in "$@"; do
  grep -q "$ioc" "$MOD" && echo "HIT: $ioc in $MOD"
done
```

### Step 4: If You Have Hits

Follow the eight steps in order.
The same outline appears in every per-ecosystem playbook so that incident response stays
consistent regardless of which registry was hit.

1. **Identify scope.** Affected machine(s), exact `go build|test|run|install` command(s)
   and time window. For tests in particular, malicious test files run on every
   `go test ./...`.
2. **Preserve evidence before cleanup.** Snapshot the module cache:
   `cp -a $(go env GOMODCACHE) /tmp/audit-snapshot-gomod-$(date +%s)`, save `~/.netrc`,
   the offending `go.mod` / `go.sum` / `go.work`, and shell history.
3. **Rotate tokens by category.** GitHub PAT/OAuth (`~/.config/gh`); SSH (`~/.ssh/*`);
   cloud (`~/.aws/credentials`, `~/.config/gcloud/`, Azure CLI); env-var API keys.
   Go modules execute on `go test` and on `go run`; assume any secret reachable from
   those processes was potentially exfiltrated.
4. **Check persistence mechanisms specific to this payload.** The Rekoobe backdoor (fake
   `x/crypto`) installs an SSH-accessible backdoor on Linux; check
   `~/.ssh/authorized_keys`, `/etc/ssh/sshd_config`, and unusual listening ports
   (`ss -lntp`). The 2025 disk-wiper modules execute `dd if=/dev/zero of=/dev/sda`; on a
   non-wiped system, look for the wiper script in `/tmp` and recent unsuccessful
   execution attempts in audit logs.
   Always check `cron`, `systemctl --user list-unit-files --state=enabled`, and
   `launchctl list` on macOS.
5. **Remove or downgrade the affected dependency.** Replace the malicious module path
   with the legitimate one in `go.mod` (and any `go.work`). Run `go mod tidy` to clean
   up `go.sum`.
6. **Regenerate lockfile from trusted sources.** Force fresh checksums:
   `GOPROXY=https://proxy.golang.org,direct go mod download -x` to ensure modules come
   from the trusted public proxy, then `go mod verify`.
7. **Re-run the scanner to confirm clean.** `govulncheck ./...` and
   `osv-scanner scan source --lockfile=go.mod`. Treat any remaining `[MALICIOUS]`
   advisory as a failed cleanup.
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
Inject the variables explicitly.

### GitHub Actions

```yaml
env:
  GOPROXY: "https://proxy.golang.org,direct"
  GOSUMDB: "sum.golang.org"
  GONOSUMDB: ""
  GOFLAGS: "-mod=readonly"
  GOVULNCHECK_VERSION: "v1.1.4"
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
      - run: go install "golang.org/x/vuln/cmd/govulncheck@$GOVULNCHECK_VERSION"
      - run: govulncheck ./...
```

### GitLab CI

```yaml
variables:
  GOPROXY: "https://proxy.golang.org,direct"
  GOSUMDB: "sum.golang.org"
  GONOSUMDB: ""
  GOFLAGS: "-mod=readonly"
  GOVULNCHECK_VERSION: "v1.1.4"
build:
  script:
    - go mod verify
    - go mod tidy -diff
    - go build ./...
    - go test ./...
    - go install "golang.org/x/vuln/cmd/govulncheck@$GOVULNCHECK_VERSION"
    - govulncheck ./...
```

**Note on scanner pinning.** Pinning `GOVULNCHECK_VERSION` (rather than `@latest`)
prevents an attack on the audit pipeline itself.
For production CI, pre-install `govulncheck` into the runner image so it does not
download on every job.

## Subscribe-And-Watch Feeds

For early warning of new named attacks:

- [Go Vulnerability Database](https://pkg.go.dev/vuln/) (official, curated by the Go
  security team)
- [OSV.dev Go ecosystem](https://osv.dev/list?ecosystem=Go)
- [Socket.dev](https://socket.dev/)
- [Aikido Intel](https://intel.aikido.dev)
- [StepSecurity Blog](https://www.stepsecurity.io/blog)
- [Datadog Security Labs](https://securitylabs.datadoghq.com/)

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
