# NPM Operational Hardening

**Last updated:** 2026-05-23

**Author:** Joshua Levy (github.com/jlevy) with agent assistance

The minimum action list to harden a workstation or CI runner against the 2025-2026 npm
supply-chain attack wave, and to check whether you have already been compromised.
Full threat model, per-platform setup, IOC feeds, and scanning tools in
[research-npm-supply-chain-hardening.md](../research/research-npm-supply-chain-hardening.md).

This guide is install-side (protecting you as a *consumer*). If you also *publish* npm
packages, harden the release pipeline too: use OIDC trusted publishing instead of
long-lived tokens, enable staged publishing (`npm stage publish` / `npm stage approve`,
npm 11.15+), and follow [`hardening-ci-cd.md`](hardening-ci-cd.md).
The May 2026 @antv worm forged a valid “verified” provenance badge, so do not treat
provenance as proof.

## Hardening (Ten-Minute Setup)

### Step 1: Create The Hardening Script

The `~/.npm-hardening.sh` env-var recipe below applies to **npm (all versions) and pnpm
10.x**. **pnpm 11 changed how it reads config** (see the pnpm 11 box after the script);
if you are on pnpm 11, use the YAML recipe instead, or it will silently ignore these
`NPM_CONFIG_*` variables.

Create `~/.npm-hardening.sh` with the four protection env vars:

```sh
# Rolling 14-day install quarantine, recomputed at shell start.
# BSD date (macOS) primary; GNU date (Linux/WSL) fallback.
NPM_HARDENING_BEFORE="$(date -u -v-14d '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null \
  || date -u -d '14 days ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null)"
[ -n "$NPM_HARDENING_BEFORE" ] && export NPM_CONFIG_BEFORE="$NPM_HARDENING_BEFORE"
unset NPM_HARDENING_BEFORE

# pnpm 10.x native rolling check; 20160 = 14 days in minutes. Requires pnpm 10.16-10.x.
# (pnpm 11 ignores this name; see the pnpm 11 box below.)
export NPM_CONFIG_MINIMUM_RELEASE_AGE=20160

# Defeat install scripts. Primary exfil vector in worm-class attacks.
export NPM_CONFIG_IGNORE_SCRIPTS=true

# pnpm 10.x only: refuse mutating installs. npm warns and ignores; harmless.
# npm users: use `npm ci` (clean install) in CI and after lockfile changes; it is
# the non-mutating install mode for npm and is the equivalent of pnpm's frozen-lockfile.
export NPM_CONFIG_FROZEN_LOCKFILE=true

# pnpm 10.x only: fail when a dependency wants to run an unreviewed build script.
# Pair with `allowBuilds` in pnpm-workspace.yaml to allowlist trusted build scripts.
export NPM_CONFIG_STRICT_DEP_BUILDS=true
```

> **pnpm 11 (released 2026-04-28) reads config differently.** Per the
> [pnpm 11 release notes](https://pnpm.io/blog/releases/11.0), pnpm **no longer reads
> `npm_config_*` / `NPM_CONFIG_*` environment variables**; the env prefix is now
> `pnpm_config_*` / `PNPM_CONFIG_*` (e.g. `PNPM_CONFIG_MINIMUM_RELEASE_AGE`), and
> `.npmrc` is auth/registry only.
> Put the policy in `pnpm-workspace.yaml` (project) or `~/.config/pnpm/config.yaml`
> (global) so it cannot be silently dropped:
> 
> ```yaml
> # pnpm-workspace.yaml (or ~/.config/pnpm/config.yaml)
> minimumReleaseAge: 20160        # 14 days in minutes (default in v11 is 1440 = 1 day)
> minimumReleaseAgeExclude: []    # add per-package exceptions here (documented only)
> ignoreScripts: true             # block lifecycle scripts by default
> strictDepBuilds: true           # default true in v11; fail on unreviewed build scripts
> allowBuilds:                    # map: only these packages may run build scripts
>   esbuild: true
> ```
> 
> Run `pnpm install --frozen-lockfile` in CI for the lockfile guarantee.
> The `PNPM_CONFIG_*` env prefix works for processes that do not read the YAML, but the
> YAML is the durable, reviewable source of truth.

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
  # npm / pnpm 10.x; pnpm 11 users: use the YAML recipe in Step 1 instead.
  set -gx NPM_CONFIG_BEFORE (date -u -v-14d '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null; or date -u -d '14 days ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null)
  set -gx NPM_CONFIG_MINIMUM_RELEASE_AGE 20160
  set -gx NPM_CONFIG_IGNORE_SCRIPTS true
  set -gx NPM_CONFIG_FROZEN_LOCKFILE true
  set -gx NPM_CONFIG_STRICT_DEP_BUILDS true
  ```
- **Windows PowerShell**: add to `$PROFILE` (see
  [research-npm-supply-chain-hardening.md](../research/research-npm-supply-chain-hardening.md#powershell-7-pwsh)).
- **Linux systemd user environment**: put in
  `~/.config/environment.d/npm-hardening.conf` (see
  [research-npm-supply-chain-hardening.md](../research/research-npm-supply-chain-hardening.md#systemd-user-environment-linux-specific)).

### Step 3: Verify

```sh
# Shell-state check: every variable is set in the current shell.
env | grep -E '^NPM_CONFIG_(BEFORE|MIN_RELEASE_AGE|MINIMUM_RELEASE_AGE|IGNORE_SCRIPTS|FROZEN_LOCKFILE|STRICT_DEP_BUILDS)='

# Tool view: npm and pnpm 10.x report what they actually honor (cross-check with shell).
pnpm config get before                # ISO date ~14 days ago
pnpm config get minimum-release-age   # 20160
pnpm config get ignore-scripts        # true
pnpm config get frozen-lockfile       # true
npm config get before                 # date ~14 days ago
npm config get ignore-scripts         # true
```

`npm` warns “Unknown env config ‘frozen-lockfile’ / 'minimum-release-age'”. Those are
pnpm-only features; npm still functions correctly.

**pnpm 11 verification** (the `NPM_CONFIG_*` view above does not apply; confirm the YAML
is actually honored):

```sh
pnpm --version                     # 11.x
pnpm config get minimumReleaseAge  # 20160 (not 1440)
pnpm config get strictDepBuilds    # true
pnpm config get ignoreScripts      # true
# Smoke test: a just-published version must be refused by the 14-day gate.
pnpm add --dry-run <some-package-published-in-the-last-day> 2>&1 | head
```

Env-var-only setups are not visible to GUI-launched agents or non-interactive
subprocesses that do not inherit your shell environment.
If you run agents through a desktop launcher (Claude Code app, IDE plugins,
launchd-spawned processes), confirm the variables are present **in the agent’s own
process** with `env | grep` rather than trusting your terminal’s view.
On Linux, prefer `~/.config/environment.d/npm-hardening.conf` for systemd-launched
processes (see the research doc).

#### Names And Units Differ Between npm And pnpm

| Tool | Setting | Unit |
| --- | --- | --- |
| npm (any) | `NPM_CONFIG_BEFORE` | absolute ISO 8601 date |
| npm 11.10+ | `NPM_CONFIG_MIN_RELEASE_AGE` | days (integer) |
| pnpm 10.16-10.x | `NPM_CONFIG_MINIMUM_RELEASE_AGE` | minutes (integer) |
| pnpm 11+ | `minimumReleaseAge` in `pnpm-workspace.yaml` (env: `PNPM_CONFIG_MINIMUM_RELEASE_AGE`) | minutes (integer) |

Do not set both `NPM_CONFIG_BEFORE` and `NPM_CONFIG_MIN_RELEASE_AGE` for npm; pick one
based on your npm version.
For **pnpm 10.x**, `NPM_CONFIG_MINIMUM_RELEASE_AGE` (note the spelling: `MINIMUM`, not
`MIN`) is safe to set alongside `BEFORE`; pnpm enforces the stricter of the two.
For **pnpm 11**, none of the `NPM_CONFIG_*` names are read at all; use the YAML config
(or the `PNPM_CONFIG_*` env prefix) from the Step 1 pnpm 11 box.

### Agent Ban List

Do not run `npx`, `pnpm dlx`, `bunx`, or `yarn dlx` without an explicit version pin and
a review of the resolved `pkg@version`. These tools fetch and execute the latest
published code, bypassing your cool-off window.
Use `pnpm dlx <pkg>@<exact-version>` and read the resolved version before allowing
execution. Full agent rules are in [`../AGENTS.md`](../AGENTS.md) → “Safety Rule For
Agents”.

For untrusted first-runs, see
[`untrusted-repo-first-run.md`](untrusted-repo-first-run.md).

### Step 4: When You Intentionally Need A Fresh Package

Unset the quarantine env vars per command, visibly.
Cover both naming variants because you may not remember which is honored by your tool
version:

```sh
NPM_CONFIG_BEFORE= NPM_CONFIG_MIN_RELEASE_AGE=0 NPM_CONFIG_MINIMUM_RELEASE_AGE=0 \
  NPM_CONFIG_FROZEN_LOCKFILE=false pnpm add some-pkg
```

This is the documented [exception process](../README.md#the-exception-process): take it
only with a stated reason (a CVE ID for security patches), pin the exact version, and
log it. The env vars above enforce the 14-day default; everything below helps you hold
the line at upgrade time.

### Step 5: Enforce The 14-Day Cool-Off At Upgrade Time

`NPM_CONFIG_MINIMUM_RELEASE_AGE` gates resolution; `npm-check-updates --cooldown` gates
the upgrade decision itself.
Use it (works on npm/pnpm/yarn projects):

```sh
# Refuse any candidate version younger than 14 days
pnpm dlx npm-check-updates@<pinned-version> --cooldown 14

# CI-style: exit non-zero if any fresh-enough upgrade is available
pnpm dlx npm-check-updates@<pinned-version> --cooldown 14 --errorLevel 2
```

For a specific version, query the publish time directly and wait if it is too new:

```sh
npm view <pkg> time            # all publish times
npm view <pkg> time.<version>  # one version; if < 14 days ago, wait
```

Optional pre-push guard that fails if any direct dependency is younger than 14 days:

```sh
#!/usr/bin/env bash
# scripts/check-package-age.sh — wire into a pre-push hook (lefthook/husky).
COOLDOWN_DAYS=14
now=$(date -u +%s)
fail=0
node -e 'const p=require("./package.json");for(const[n,v]of Object.entries({...p.dependencies,...p.devDependencies}))console.log(n,String(v).replace(/^[^0-9]*/,""))' \
| while read -r name version; do
    published=$(npm view "$name@$version" time."$version" 2>/dev/null) || continue
    [ -z "$published" ] && continue
    age=$(( (now - $(date -u -d "$published" +%s 2>/dev/null || date -u -jf '%Y-%m-%dT%H:%M:%S' "${published%.*}" +%s)) / 86400 ))
    if [ "$age" -lt "$COOLDOWN_DAYS" ]; then echo "✗ $name@$version is only ${age}d old (< $COOLDOWN_DAYS)"; fail=1; fi
  done
exit $fail
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

The most relevant attacks as of 2026-05-23. Canonical full list (cross-ecosystem) is in
[`compromised-packages.md`](../compromised-packages.md); this is the npm quick-grep
extract:

| Date | Name | Quick IOC Pattern |
| --- | --- | --- |
| 2026-05-19 | @antv (Mini Shai-Hulud) | `@antv/g@6.4.1`, `@antv/g@6.5.1`, `echarts-for-react@3.1.7`, `size-sensor@1.0.4`; full list via GitHub Advisory DB `type:malware` for the `atool` scope (e.g. `GHSA-6fr3-r6r6-h4h9`). Note: forged “verified” provenance, badge is not proof |
| 2026-05-18 | Megalodon / Tiledesk | `@tiledesk/tiledesk-server@2.18.6`, `2.18.7`, `2.18.9`, `2.18.10`, `2.18.11`, `2.18.12` (clean `2.18.5`); see [GHSA-5vfv-hpg7-77hj](https://github.com/advisories/GHSA-5vfv-hpg7-77hj) |
| 2026-05-14 | node-ipc | `node-ipc@9.1.6`, `node-ipc@9.2.3`, `node-ipc@12.0.1`. Fires at `require()`, not via install script, so `ignore-scripts` does not block it |
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

Follow the eight steps in order.
Items marked “ecosystem-specific” describe what to do for npm; the same eight-step
outline appears in every per-ecosystem playbook so that incident response stays
consistent regardless of which registry was hit.

1. **Identify scope.** Affected machine(s), the exact command(s) and time window when
   the malicious version was installed.
   Get this before any cleanup; you will need it for credential rotation and incident
   reporting.
2. **Preserve evidence before cleanup.** Snapshot the install state:
   `cp -a $(npm root -g) /tmp/audit-snapshot-npm-global-$(date +%s)`, capture `~/.npmrc`
   / `~/.bash_history`, save `npm config list --json`, `gh api /user` output, and any
   active OSV-scanner output.
   Commit these into the private audit log before mutating anything.
3. **Rotate tokens by category.** npm tokens (`npm token list`, then revoke); GitHub PAT
   and OAuth (Settings → Developer settings, and `gh api /user/runners` to look for
   persistence); cloud (`~/.aws/credentials`, `~/.config/gcloud/`, Azure CLI); SSH
   (`~/.ssh/*`); any env-var-stored API keys.
4. **Check persistence mechanisms specific to this payload.** Shai-Hulud 2.0 registers a
   self-hosted GitHub runner literally named `SHA1HULUD`; check `gh api /user/runners`
   and `gh api /orgs/<org>/actions/runners`. qix / browser-hijack variants do not have
   persistence; worm variants do.
   Look at `~/.bash_history`, recent `crontab -l`, `launchctl list` (macOS), and
   `systemctl --user list-unit-files --state=enabled` (Linux).
5. **Remove or downgrade the affected dependency.** Pin to the immediately-prior version
   in `package.json`, then `pnpm install --before=<date-of-known-good>` or `npm ci`
   against a clean lockfile.
   Commit.
6. **Regenerate lockfile from trusted sources.** Delete `node_modules/`, delete
   `package-lock.json` / `pnpm-lock.yaml`, run the install against the cool-off window
   in effect. Commit the regenerated lockfile.
7. **Re-run the scanner to confirm clean.** `osv-scanner scan -L pnpm-lock.yaml` (or
   `package-lock.json`) and `uv run scripts/audit_npm.py` if the hit was on a global
   tool. Exit 3 means `[MALICIOUS]` still present; treat 0 as the only acceptable
   post-clean state.
8. **Open a `supply-chain-audit-log.md` entry** using the template (see “Keeping A
   Supply Chain Audit Log” below and
   [`../supply-chain-audit-log-template.md`](../supply-chain-audit-log-template.md)).
   Record raw findings, analysis, every action with timestamps, and any pending
   follow-ups. Redact live credentials per the template’s Redaction Rules.

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

The `NPM_CONFIG_*` env block below targets **npm and pnpm 10.x**. For **pnpm 11**,
commit the policy in `pnpm-workspace.yaml` (Step 1 box) and pass `--frozen-lockfile`;
pnpm 11 ignores `NPM_CONFIG_*`, so set `PNPM_CONFIG_*` names instead if you must use env
vars in CI.

```yaml
env:
  NPM_CONFIG_IGNORE_SCRIPTS: "true"
  NPM_CONFIG_FROZEN_LOCKFILE: "true"
  NPM_CONFIG_MINIMUM_RELEASE_AGE: "20160"   # pnpm 10.x; pnpm 11 uses pnpm-workspace.yaml
  NPM_CONFIG_STRICT_DEP_BUILDS: "true"      # pnpm 10.x; pnpm 11 reads it from YAML
  OSV_SCANNER_VERSION: "v2.0.2"
jobs:
  install:
    runs-on: ubuntu-latest
    steps:
      - name: Compute rolling quarantine
        run: echo "NPM_CONFIG_BEFORE=$(date -u -d '14 days ago' '+%Y-%m-%dT%H:%M:%SZ')" >> "$GITHUB_ENV"
      - uses: actions/checkout@v4
      - run: pnpm install --frozen-lockfile   # npm equivalent: `npm ci`
      - name: Install pinned osv-scanner
        run: |
          curl -fsSL -o /tmp/osv-scanner \
            "https://github.com/google/osv-scanner/releases/download/${OSV_SCANNER_VERSION}/osv-scanner_linux_amd64"
          chmod +x /tmp/osv-scanner
      - run: /tmp/osv-scanner scan -L pnpm-lock.yaml
```

**Note on scanner pinning.** The recipe pins `OSV_SCANNER_VERSION` instead of pulling
`@latest`. For production CI, pre-install osv-scanner into the runner image and verify
the binary checksum against the GitHub release.

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
