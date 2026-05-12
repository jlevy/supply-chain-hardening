# NPM Operational Hardening

**Last updated:** 2026-05-12

**Author:** Joshua Levy (github.com/jlevy) and LLM assistance

The minimum action list to harden a workstation or CI runner against the 2025-2026 npm supply-chain attack wave, and to check whether you have already been compromised. Full threat model, per-platform setup, IOC feeds, and scanning tools in [research-npm-supply-chain-hardening.md](research-npm-supply-chain-hardening.md).

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

Pick the line for every shell you use. Detail on each in [research-npm-supply-chain-hardening.md](research-npm-supply-chain-hardening.md#part-3-best-practices-for-hardening).

- **zsh** (any OS): add to `~/.zshenv`
  `[ -r "$HOME/.npm-hardening.sh" ] && . "$HOME/.npm-hardening.sh"`
- **bash, interactive** (any OS): add the same line to `~/.bashrc`.
- **bash, login** (macOS Terminal default, SSH sessions): add the same line to `~/.bash_profile` or `~/.profile`.
- **fish**: add to `~/.config/fish/conf.d/npm-hardening.fish`:
  ```fish
  set -gx NPM_CONFIG_BEFORE (date -u -v-7d '+%Y-%m-%dT%H:%M:%SZ')
  set -gx NPM_CONFIG_MINIMUM_RELEASE_AGE 10080
  set -gx NPM_CONFIG_IGNORE_SCRIPTS true
  set -gx NPM_CONFIG_FROZEN_LOCKFILE true
  ```
- **Windows PowerShell**: add to `$PROFILE` (see [research-npm-supply-chain-hardening.md](research-npm-supply-chain-hardening.md#powershell-7-pwsh)).
- **Linux systemd user environment**: put in `~/.config/environment.d/npm-hardening.conf` (see [research-npm-supply-chain-hardening.md](research-npm-supply-chain-hardening.md#systemd-user-environment-linux-specific)).

### Step 3: Verify

```sh
pnpm config get before                # ISO date ~7 days ago
pnpm config get minimum-release-age   # 10080
pnpm config get ignore-scripts        # true
pnpm config get frozen-lockfile       # true
npm config get before                 # date ~7 days ago
npm config get ignore-scripts         # true
```

`npm` warns "Unknown env config 'frozen-lockfile' / 'minimum-release-age'". Those are pnpm-only features; npm still functions correctly.

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
osv-scanner -L pnpm-lock.yaml
osv-scanner -L package-lock.json
osv-scanner -L yarn.lock
```

### Step 2: Grep For Known IOCs From The Most Recent Named Attacks

The most relevant attacks as of 2026-05-12 (full table with all packages and versions in [research-npm-supply-chain-hardening.md](research-npm-supply-chain-hardening.md#part-2-notable-exploits-to-be-aware-of)):

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

1. **Revoke every credential reachable** from any machine that ran `pnpm install`, `npm install`, or `yarn install` while the malicious version was the latest. Cover: npm tokens (`npm token list`), GitHub tokens (`~/.config/gh/`, GitHub Settings → Developer settings), cloud creds (`~/.aws/credentials`, `~/.config/gcloud/`), and any env-var-stored API keys.
2. **Downgrade to the immediately-prior version** in `package.json`, then `pnpm install --before=<date-of-known-good>`. Commit.
3. **Inspect `~/.npmrc`, `~/.gitconfig`, `~/.bash_history`, and shell history** for exfiltrated content or unexpected modifications.
4. **Treat the developer machine as potentially compromised** for the persistence variants (Shai-Hulud 2.0 registers a self-hosted GitHub runner named `SHA1HULUD`; check `gh api /user/runners`).

## CI Enforcement

CI environments do not source user shell init. Inject the variables explicitly.

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
      - run: osv-scanner -L pnpm-lock.yaml
```

Other CI: see [research-npm-supply-chain-hardening.md](research-npm-supply-chain-hardening.md#setup-ci-runners) for GitLab, CircleCI, Buildkite, Jenkins.

## Subscribe-And-Watch Feeds

For early warning of new named attacks:

- [Aikido Intel](https://www.aikido.dev/intel)
- [StepSecurity Blog](https://www.stepsecurity.io/blog) (often the first public detector)
- [Unit 42 living doc](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/)
- [Socket.dev](https://socket.dev/)
- [Datadog Security Labs](https://securitylabs.datadoghq.com/)

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
