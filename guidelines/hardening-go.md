# Go Modules Operational Hardening

**Last updated:** 2026-05-12

**Author:** Joshua Levy (github.com/jlevy) and LLM assistance

The minimum action list to harden a workstation or CI runner against Go module
supply-chain attacks, and to check whether you have already been compromised.
Full threat model, incident timeline, and scanning-tool comparisons in
[research-go-supply-chain-hardening.md](../research/research-go-supply-chain-hardening.md).

## Hardening (Ten-Minute Setup)

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
go env GOPROXY      # https://proxy.golang.org,direct
go env GOSUMDB      # sum.golang.org
go env GONOSUMDB # (empty)
go env GOFLAGS      # -mod=readonly
go mod verify       # all modules verified
```

### Step 4: When You Intentionally Modify Dependencies

Unset the readonly flag per command, visibly:

```sh
GOFLAGS="" go get -u github.com/some/module@v1.2.3
GOFLAGS="" go mod tidy
```

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

1. **Revoke every credential reachable** from any machine that built or ran the
   malicious module. Cover: GitHub tokens (`~/.config/gh/`), cloud creds
   (`~/.aws/credentials`, `~/.config/gcloud/`), SSH keys, and any env-var-stored API
   keys.
2. **Remove the malicious module** from `go.mod` and `go.sum`, replace with the
   legitimate module path, run `go mod tidy`, and commit.
3. **Inspect the system for persistence.** The Rekoobe backdoor installs an
   SSH-accessible backdoor on Linux.
   The disk-wiper modules execute `dd if=/dev/zero of=/dev/sda`. Check running
   processes, cron, and systemd user services.

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
      - run: go install golang.org/x/vuln/cmd/govulncheck@latest && govulncheck ./...
```

### GitLab CI

```yaml
variables:
  GOPROXY: "https://proxy.golang.org,direct"
  GOSUMDB: "sum.golang.org"
  GONOSUMDB: ""
  GOFLAGS: "-mod=readonly"
build:
  script:
    - go mod verify
    - go mod tidy -diff
    - go build ./...
    - go install golang.org/x/vuln/cmd/govulncheck@latest && govulncheck ./...
```

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
