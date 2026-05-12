# NPM Operational Hardening

**Last updated:** 2026-05-12

**Author:** Joshua Levy (github.com/jlevy) with agent assistance

The minimum action list to harden a workstation or CI runner against the 2025-2026 npm
supply-chain attack wave, and to check whether you have already been compromised.
Full threat model, per-platform setup, IOC feeds, and scanning tools in
[research-npm-supply-chain-hardening.md](../research/research-npm-supply-chain-hardening.md).

## Hardening (Ten-Minute Setup)

### Step 1: Create The Hardening Script

Create `~/.npm-hardening.sh` with the four protection env vars:

```sh
# Rolling 7-day install quarantine, recomputed at shell start.
# BSD date (macOS) primary; GNU date (Linux/WSL) fallback.
NPM_HARDENING_BEFORE="$(date -u -v-7d '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null \
  || date -u -d '7 days ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null)"
[ -n "$NPM_HARDENING_BEFORE" ] && export NPM_CONFIG_BEFORE="$NPM_HARDENING_BEFORE"
unset NPM_HARDENING_BEFORE

# pnpm-native rolling check; 10080 = 7 days in minutes. Requires pnpm >= 10.16.0.
export NPM_CONFIG_MINIMUM_RELEASE_AGE=10080

# Defeat install scripts. Primary exfil vector in worm-class attacks.
export NPM_CONFIG_IGNORE_SCRIPTS=true

# pnpm only: refuse mutating installs. npm warns and ignores; harmless.
export NPM_CONFIG_FROZEN_LOCKFILE=true
```

### Step 2: Source From Shell Init

Pick the line for every shell you use.
Detail on each in
[research-npm-supply-chain-hardening.md](../research/research-npm-supply-chain-hardening.md#part-3-best-practices-for-hardening).

- **zsh** (any OS): add to `~/.zshenv`
  `[ -r "$HOME/.npm-hardening.sh" ] && . "$HOME/.npm-hardening.sh"`
- **bash, interactive** (any OS): add the same line to `~/.bashrc`.
- **bash, login** (macOS Terminal default, SSH sessions): add the same line to
  `~/.bash_profile` or `~/.profile`.
- **fish**: add to `~/.config/fish/conf.d/npm-hardening.fish`:
  ```fish
  set -gx NPM_CONFIG_BEFORE (date -u -v-7d '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null; or date -u -d '7 days ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null)
  set -gx NPM_CONFIG_MINIMUM_RELEASE_AGE 10080
  set -gx NPM_CONFIG_IGNORE_SCRIPTS true
  set -gx NPM_CONFIG_FROZEN_LOCKFILE true
  ```
- **Windows PowerShell**: add to `$PROFILE` (see
  [research-npm-supply-chain-hardening.md](../research/research-npm-supply-chain-hardening.md#powershell-7-pwsh)).
- **Linux systemd user environment**: put in
  `~/.config/environment.d/npm-hardening.conf` (see
  [research-npm-supply-chain-hardening.md](../research/research-npm-supply-chain-hardening.md#systemd-user-environment-linux-specific)).

### Step 3: Verify

```sh
pnpm config get before                # ISO date ~7 days ago
pnpm config get minimum-release-age   # 10080
pnpm config get ignore-scripts        # true
pnpm config get frozen-lockfile       # true
npm config get before                 # date ~7 days ago
npm config get ignore-scripts         # true
```

`npm` warns “Unknown env config ‘frozen-lockfile’ / 'minimum-release-age'”. Those are
pnpm-only features; npm still functions correctly.

### Step 4: When You Intentionally Need A Fresh Package

Unset the quarantine env vars per command, visibly:

```sh
NPM_CONFIG_BEFORE= NPM_CONFIG_MINIMUM_RELEASE_AGE=0 NPM_CONFIG_FROZEN_LOCKFILE=false pnpm add some-pkg
```

## Compromise Assessment

### Step 1: Scan Every Lockfile

```sh
# Install once: https://github.com/google/osv-scanner/releases
osv-scanner scan source -r .

# Or per-lockfile:
osv-scanner scan -L pnpm-lock.yaml
osv-scanner scan -L package-lock.json
osv-scanner scan -L yarn.lock
```

For **globally-installed packages** there is no lockfile to scan.
Use the Python script in this repo, which walks the global `node_modules` tree and
queries OSV directly.
Zero third-party dependencies; runnable with `uv run` (preferred) or `python3`:

```sh
# After `npm install -g <anything>`, back-check the global tree:
uv run scripts/audit_npm.py
# or, without uv:
python3 scripts/audit_npm.py

# Check a specific package@version pair without a directory scan:
uv run scripts/audit_npm.py --packages chalk@5.6.1 debug@4.4.2
```

See [scripts/README.md](../scripts/README.md) for full usage, exit codes, and the
rationale for using a Python-stdlib script rather than a Node-based one.

### Step 2: Grep For Known IOCs From The Most Recent Named Attacks

The most relevant attacks as of 2026-05-12. Canonical full list (cross-ecosystem) is in
[`compromised-packages.md`](../compromised-packages.md); this is the npm quick-grep
extract:

| Date | Name | Quick IOC Pattern |
| --- | --- | --- |
| 2026-05-11 | TanStack | `@tanstack/*` packages published 19:20-19:26 UTC; canonical list at [TanStack postmortem](https://tanstack.com/blog/npm-supply-chain-compromise-postmortem) |
| 2026-04-30 | Intercom and lightning | `intercom-client@7.0.4`, `intercom-client@7.0.5`, `lightning@2.6.2`, `lightning@2.6.3` |
| 2026-04-29 | SAP / `@cap-js/*` | `mbt@1.2.48`, `@cap-js/db-service@2.10.1`, `@cap-js/postgres@2.2.2`, `@cap-js/sqlite@2.2.2` |
| 2026-03-31 | Axios | `axios@1.14.1`, `axios@0.30.4` |
| 2025-11-24 | Shai-Hulud 2.0 | 796 packages; full IOC JSON at `https://blog.ehsan.it/shai-hulud-v2-ioc.json` |
| 2025-09-15 | Shai-Hulud 1.0 | `@ctrl/tinycolor@4.1.1/4.1.2`, `ngx-bootstrap`, `angulartics2`, many `@ctrl/*` |
| 2025-09-08 | qix maintainer phish | `chalk@5.6.1`, `debug@4.4.2`, `ansi-styles@6.2.2`, `supports-color@10.2.1`, plus 15 others |

Quick grep template for a single IOC:

```sh
#!/usr/bin/env bash
# Usage: scan-iocs.sh /path/to/lockfile  ioc1@ver  ioc2@ver ...
LOCK="$1"; shift
for ioc in "$@"; do
  pkg="${ioc%@*}"; ver="${ioc##*@}"
  case "$LOCK" in
    *pnpm-lock.yaml)    grep -qE "['/]${pkg}@${ver}[:'(]" "$LOCK" && echo "HIT: $ioc" ;;
    *package-lock.json) grep -B1 "\"version\": \"${ver}\"" "$LOCK" | grep -q "\"node_modules/${pkg}\"" && echo "HIT: $ioc" ;;
    *yarn.lock)         grep -qE "^\"?${pkg}@${ver}\"?:" "$LOCK" && echo "HIT: $ioc" ;;
  esac
done
```

### Step 3: If You Have Hits

1. **Revoke every credential reachable** from any machine that ran `pnpm install`,
   `npm install`, or `yarn install` while the malicious version was the latest.
   Cover: npm tokens (`npm token list`), GitHub tokens (`~/.config/gh/`, GitHub Settings
   → Developer settings), cloud creds (`~/.aws/credentials`, `~/.config/gcloud/`), and
   any env-var-stored API keys.
2. **Downgrade to the immediately-prior version** in `package.json`, then
   `pnpm install --before=<date-of-known-good>`. Commit.
3. **Inspect `~/.npmrc`, `~/.gitconfig`, `~/.bash_history`, and shell history** for
   exfiltrated content or unexpected modifications.
4. **Treat the developer machine as potentially compromised** for the persistence
   variants (Shai-Hulud 2.0 registers a self-hosted GitHub runner named `SHA1HULUD`;
   check `gh api /user/runners`).

## Keeping A Supply Chain Audit Log

Every audit run leaves a record.
A consistent log lets a future reader (human or agent) reconstruct exactly what was
checked, what was found, how each finding was analysed, and what action was taken.
It also prevents an agent in a fresh session from re-deriving the same conclusions from
scratch.

### Where To Put It

Maintain a file named `supply-chain-audit-log.md` in one of two locations:

- **In each developer-tools repo** (recommended for personal hardening work): a single
  file per developer machine that tracks audits of that machine’s global tooling.
- **In a project repo** (recommended for shared-project audits): tracks audits of that
  project’s lockfiles.

Start from the [template](../supply-chain-audit-log-template.md) in this repository.
The template is committed; `supply-chain-audit-log.md` itself is gitignored at this
repo’s root because real audit logs typically contain machine-specific paths, package
versions tied to a single developer’s tooling, and similar details that should not be
redistributed.

### What To Record

Every audit run gets an entry.
Use the headings below, in order.
Keep empty sections (write “(none)”) rather than omitting them so the format stays
consistent across entries.

```
## YYYY-MM-DD — Short Title

### Context
(Machine state, hardening configuration, auditor)

### Scope
(What was scanned)

### Commands Run
(Verbatim, reproducible)

### Raw Findings
(Numbers and identifying details, before analysis)

### Analysis And Verdict
(One subsection per finding that needed thought; clear final call)

### Actions Taken
(What was done in response to findings, with timestamps)

### Pending Actions
(Outstanding follow-ups, with owner)

### Verdict (Summary)
(One paragraph summarising the audit outcome)
```

### Rules For Agents Updating The Log

1. **Append, do not rewrite.** New entries go at the top (reverse chronological).
   Earlier entries stay intact as historical record.
2. **Quote raw outputs.** Include exact command output snippets, not paraphrased
   summaries. Numbers must match the script output exactly.
3. **Document false positives explicitly.** When a hit turns out to be a false positive
   after analysis, the analysis path goes in `### Analysis And Verdict`. Do not silently
   drop the finding from `### Raw Findings`.
4. **Record every action with a timestamp.** Patches to scripts, version bumps,
   credential rotations — all in `### Actions Taken` with the time and outcome.
5. **Move incomplete items to `### Pending Actions`.** Empty `Pending Actions` is fine
   and explicit; missing section is not.

### When To Open A New Entry

- After every `audit_npm.py` run, or any `osv-scanner` run that surfaces hits.
- After installing or upgrading a globally-scoped npm tool (`npm install -g`,
  `pnpm add -g`).
- After receiving an attack disclosure from a Tier-2 feed (Aikido, StepSecurity, Unit
  42, Socket, Datadog Security Labs) that mentions a package family relevant to your
  installed tools.
- After remediation: revoking credentials, downgrading packages, removing tools.

## CI Enforcement

CI environments do not source user shell init.
Inject the variables explicitly.

### GitHub Actions

```yaml
env:
  NPM_CONFIG_IGNORE_SCRIPTS: "true"
  NPM_CONFIG_FROZEN_LOCKFILE: "true"
  NPM_CONFIG_MINIMUM_RELEASE_AGE: "10080"
jobs:
  install:
    runs-on: ubuntu-latest
    steps:
      - name: Compute rolling quarantine
        run: echo "NPM_CONFIG_BEFORE=$(date -u -d '7 days ago' '+%Y-%m-%dT%H:%M:%SZ')" >> "$GITHUB_ENV"
      - uses: actions/checkout@v4
      - run: pnpm install
      - run: osv-scanner scan -L pnpm-lock.yaml
```

Other CI: see
[research-npm-supply-chain-hardening.md](../research/research-npm-supply-chain-hardening.md#setup-ci-runners)
for GitLab, CircleCI, Buildkite, Jenkins.

## Subscribe-And-Watch Feeds

For early warning of new named attacks:

- [Aikido Intel](https://intel.aikido.dev)
- [StepSecurity Blog](https://www.stepsecurity.io/blog) (often the first public
  detector)
- [Unit 42 living doc](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/)
- [Socket.dev](https://socket.dev/)
- [Datadog Security Labs](https://securitylabs.datadoghq.com/)

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
