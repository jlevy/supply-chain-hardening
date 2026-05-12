# NPM Supply Chain Hardening

**Last updated:** 2026-05-12

**Author:** Joshua Levy (github.com/jlevy) and LLM assistance

A working guide for locking down `npm`, `pnpm`, `yarn`, and `bun` on developer workstations and CI runners against the 2025-2026 supply-chain attack wave. Includes concrete configuration recipes, per-platform and per-shell setup, indicator-of-compromise (IOC) feeds, and local scanning tools.

The doc has three parts:

1. **Background**: why this matters and the pattern these attacks share.
2. **Notable Exploits**: the named incidents from August 2025 through May 2026, with affected packages and dates so you can spot-check installed lockfiles.
3. **Best Practices for Hardening**: copy-pasteable configuration for every major package manager, broken out by platform and shell.

A self-update section at the end describes when to refresh content and which authoritative sources to verify against.

## Scope

**In scope:** developer-workstation and CI-runner hardening for the npm ecosystem. Configuration of `npm` (≥11), `pnpm` (≥10.16), `yarn` classic (1.x), `yarn` berry (2.x+), and `bun`. IOC feeds and local scanners. Cross-platform: macOS, Linux (Debian/Ubuntu/RHEL family), Windows (PowerShell, cmd, Git Bash, WSL).

**Out of scope:** server-side npm registry mirroring (Verdaccio, JFrog Artifactory, Sonatype Nexus). Container image scanning. Runtime SBOM tracking. GitHub Actions `pull_request_target` mitigation (referenced briefly in attack-mechanism context only).

---

# Part 1: Background

The npm ecosystem has been under sustained, accelerating supply-chain attack since August 2025. Recent waves use self-replicating worms that, after a single developer-credential phish, compromise hundreds of packages in hours via GitHub Actions trust boundaries and trusted-publisher flows. The most recent named incident at the time of writing, **TanStack on 2026-05-11**, pushed 84 malicious versions across 42 `@tanstack/*` packages within a six-minute window before detection.

## What The Attacks Have In Common

Across every named incident in the 2025-2026 wave, the playbook collapses to three primitives:

1. **Account takeover of a high-value maintainer.** Phishing (qix, via a fake `npmjs.help` 2FA-reset email), GitHub Actions exploitation (TanStack, via `pull_request_target` "Pwn Request" with cache poisoning and OIDC token theft from runner memory), or token theft from prior victims.
2. **Publication of malicious versions to packages the victim owns.** Frequently high-download libraries (`chalk` at ~50M weekly downloads, `axios` at ~70M, `@ctrl/tinycolor` at ~2.2M, `@tanstack/react-router` at ~12M).
3. **Credential exfiltration or runtime browser hijack.** Worm-pattern attacks (Shai-Hulud 1.0/2.0, SAP wave, TanStack) exfiltrate `~/.npmrc`, `~/.aws/`, `~/.config/gh`, and environment-variable secrets. Browser-hijack attacks (qix wave) hook `window.fetch`, `XMLHttpRequest`, and `window.ethereum.request` to rewrite cryptocurrency wallet addresses.

**Common lifetime:** malicious versions live for minutes to a few hours before researchers detect them, the package is yanked or deprecated, and a clean version replaces it. A 7-day rolling quarantine is disproportionately effective: by the time a quarantined version becomes old enough to install, every named incident below has already been remediated by the upstream maintainer or by npm.

## Why Standard Practices Are Not Enough

- **`npm audit` and `pnpm audit`** rely on GitHub Security Advisories, populated *after* malicious versions are detected. They tell you what to remove, not what to never install in the first place.
- **Lockfiles** pin to an exact version, including a malicious one if it was the latest when `pnpm install` ran.
- **`ignore-scripts` alone** defeats worm-class attacks but does nothing against browser-runtime hijack (qix). The full pattern needs multiple controls.
- **Project-local `.npmrc`** overrides user-level config silently. A third-party repo cloned from GitHub can ship a `before=` override or a scoped-registry redirect. Environment variables are the only setting that beats project `.npmrc` in npm's precedence chain.

---

# Part 2: Notable Exploits To Be Aware Of

Every entry below is a confirmed, multi-source-reported incident. Use this table to spot-check lockfiles for known-bad `package@version` pairs.

| Date | Name | Scale | Affected Packages (Representative) | Vector |
| --- | --- | --- | --- | --- |
| 2025-08 | **Nx packages** | ~10 packages | `nx@21.5.0`–`21.5.3`, `@nx/devkit@21.5.0`–`21.5.3`, `@nx/enterprise-cloud@3.2.0`, `@nx/eslint@21.5.0`, `@nx/js@21.5.0/.1`, `@nx/key@3.2.0`, `@nx/node@21.5.0`, `@nx/workspace@21.5.0` | Maintainer-account compromise; stole npm and GitHub tokens |
| 2025-09-08 | **"qix" maintainer phish** | 18+ packages, billions of weekly downloads combined; live ~2 hours | `ansi-styles@6.2.2`, `debug@4.4.2`, `chalk@5.6.1`, `supports-color@10.2.1`, `strip-ansi@7.1.1`, `ansi-regex@6.2.1`, `wrap-ansi@9.0.1`, `color-convert@3.1.1`, `color-name@2.0.1`, `is-arrayish@0.3.3`, `slice-ansi@7.1.1`, `error-ex@1.3.3`, `simple-swizzle@0.2.3`, `supports-hyperlinks@4.1.1`, `chalk-template@1.1.1`, `backslash@0.2.1`, `color-string@2.1.1`, `has-ansi@6.0.1`, `proto-tinker-wc@0.1.87` | Phishing via fake `npmjs.help` domain; collected user/pass/TOTP |
| 2025-09-15 | **Shai-Hulud 1.0** worm | 500+ packages, ~180 confirmed | `@ctrl/tinycolor@4.1.1/4.1.2` (initial vector), `ngx-bootstrap`, `ng2-file-upload`, `angulartics2`, many `@ctrl/*` packages | Self-replicating worm; stole maintainer tokens; auto-published to other packages owned by each victim |
| 2025-11-24 | **Shai-Hulud 2.0** | 796 packages, ~25K repos, ~350 maintainers | Worm pattern continues; full list at IOC feed | Same worm plus `preinstall` script invoking `setup_bun.js` / `bun_environment.js`; registers self-hosted GitHub runner named `SHA1HULUD` for persistence |
| 2026-03-?? | Aqua Trivy compromise | Single scanner package | Trivy npm package | Attributed to "TeamPCP" actor group |
| 2026-03-31 | **Axios** | 2 versions, ~70M weekly downloads | `axios@1.14.1`, `axios@0.30.4` | Attributed to Sapphire Sleet (DPRK); pulls 2nd-stage RAT |
| 2026-04 | Bitwarden CLI | Single package | `@bitwarden/cli` (specific versions) | "TeamPCP" |
| 2026-04-29 | **SAP / `@cap-js/*`** (Mini Shai-Hulud) | ~572K weekly downloads combined | `mbt@1.2.48`, `@cap-js/db-service@2.10.1`, `@cap-js/postgres@2.2.2`, `@cap-js/sqlite@2.2.2` | Worm pattern; harvests AWS/GCP/Azure/k8s/Vault/GitHub/npm credentials |
| 2026-04-30 | Intercom and lightning | 4 versions | `intercom-client@7.0.4`, `intercom-client@7.0.5`, `lightning@2.6.2`, `lightning@2.6.3` | Same payload as SAP wave |
| 2026-05-11 | **TanStack** | 84 versions across 42 `@tanstack/*` packages; 19:20-19:26 UTC (six-minute window) | `@tanstack/react-router` plus 41 other `@tanstack/*`; full list in postmortem | `pull_request_target` "Pwn Request" plus GitHub Actions cache poisoning plus OIDC token theft from runner memory; "TeamPCP" |

**Reading this table:** if any `package@version` pair above appears in a lockfile, you almost certainly need to (1) rotate every credential reachable from any machine that ran `pnpm install` while the malicious version was the latest, and (2) downgrade to the immediately-prior version. For example: `axios@1.14.0` not `1.14.1`, `debug@4.4.1` not `4.4.2`, `chalk@5.6.0` not `5.6.1`.

**Trend line:** through April 2026, attacks were roughly monthly. May 2026 saw two within a week. The 7-day quarantine pattern in Part 3 was designed around this cadence; the next attack will almost certainly fit the same profile.

---

# Part 3: Best Practices For Hardening

## How NPM/PNPM Config Precedence Works

This is the single most important fact in the document, because the entire "override project-local `.npmrc`" requirement depends on it.

```
HIGHEST PRIORITY  →  command-line flag (--before, --ignore-scripts, etc.)
                  →  environment variable (NPM_CONFIG_* or npm_config_*)
                  →  project ./.npmrc (the one in the repo you are cwd'd into)
                  →  user ~/.npmrc
                  →  global $PREFIX/etc/npmrc
LOWEST PRIORITY   →  npm builtin defaults
```

Both `npm` and `pnpm` honor this order. Implications:

- Settings in `~/.npmrc` can be silently overridden by any project-local `.npmrc`, including ones that arrive via `git clone` of a third-party repo.
- Environment variables cannot be overridden by any `.npmrc` file. Only an explicit command-line flag beats them, and explicit flags are visible to the user running the command.
- `NPM_CONFIG_` is the documented prefix; both uppercase and lowercase (`npm_config_`) work. Dashes in the config name become underscores in the variable name (`minimum-release-age` becomes `NPM_CONFIG_MINIMUM_RELEASE_AGE`).

**Operational conclusion:** set hardening as environment variables, not as `~/.npmrc` entries. Use `.npmrc` only as a fallback for processes that do not source shell init (for example, launchd-spawned background agents).

## The Four-Control Hardening Pattern

Each control attacks a different stage of the kill chain. Apply all four.

### Control 1: `NPM_CONFIG_BEFORE` (Date-Pinned Cutoff)

Refuses to install any version published after the given ISO-8601 timestamp. Supported by both `npm` and `pnpm`. Compute dynamically as "now minus 7 days" so it slides forward with the calendar.

- **Catches:** every recent attack. Malicious versions are detected within minutes-to-hours and yanked, but they remain "published after my cutoff" for 7+ days regardless.
- **Bypass per command:** `NPM_CONFIG_BEFORE= pnpm install`, or `pnpm install --before=2026-06-01T00:00:00Z` for an explicit date.

### Control 2: `NPM_CONFIG_MINIMUM_RELEASE_AGE` (Rolling Window, pnpm Only)

Native pnpm feature added in **pnpm 10.16.0**, released Q3 2025 in direct response to the qix incident. Value is in minutes; `10080` is 7 days. Unlike `before=`, this is a per-version property: a version published 6 days ago is rejected even after the system clock advances another day, until that *version* turns 7 days old. pnpm checks each candidate version individually.

- **Catches:** the same surface as `before=`, but strictly stronger for pnpm. Survives clock skew, does not drift if the variable stops being refreshed, does not need recomputation at shell start.
- **Bypass per package:** add to `minimumReleaseAgeExclude` in `.npmrc`. For example, to exempt your own workspace packages: `minimum-release-age-exclude[]=@my-org/*`.
- **npm support:** none as of npm 11. npm warns "Unknown env config" but still functions. Use `before=` for npm.

### Control 3: `NPM_CONFIG_IGNORE_SCRIPTS` (No Install Hooks)

Refuses to run `preinstall`, `install`, `postinstall`, `prepublish`, and `prepare` scripts from any package. This is the actual exfil mechanism in every worm-class attack (Shai-Hulud 1.0/2.0, SAP wave, TanStack). The browser-hijack class (qix) does not depend on install scripts, but most other attacks do.

- **Caveat:** breaks legitimate postinstall users such as `lefthook`, `husky`, `esbuild`, `swc`, `sharp`, `canvas`, `node-gyp`-based packages, `puppeteer`, `playwright`, and `cypress`. See "Pinning Install Scripts" below for opt-in allowlist patterns.
- **Bypass per command:** `NPM_CONFIG_IGNORE_SCRIPTS=false pnpm install` inside a workspace you trust. Knowingly opt out, never by default.

### Control 4: `NPM_CONFIG_FROZEN_LOCKFILE` (pnpm) or `npm ci` (npm)

pnpm refuses `pnpm install` if it would modify the lockfile. Equivalent of `npm ci`. Forces every dependency change to be an explicit, intentional human action.

- **Catches:** transitive-dep version drift if a sub-dep re-resolves to a brand-new bad version during a normal `install`.
- **Bypass:** `NPM_CONFIG_FROZEN_LOCKFILE=false pnpm add some-pkg` when intentionally adding or upgrading.
- **npm:** no environment variable for this. Use `npm ci` instead of `npm install` for non-mutating installs, and `npm install <pkg>` only when mutating.

## Per-Package-Manager Coverage Matrix

| Control | npm 11 | pnpm ≥10.16 | yarn 1.x (classic) | yarn 2+ (berry) | bun |
| --- | :-: | :-: | :-: | :-: | :-: |
| `before=` (fixed-date pin) | ✓ | ✓ | ✗ | ✗ (open issue) | ✗ |
| `minimumReleaseAge` (rolling) | ✗ (warns and ignores) | ✓ native | ✗ | ✗ | ✗ |
| `ignore-scripts` | ✓ | ✓ | ✓ (`--ignore-scripts` flag or `ignore-scripts` rc) | ✓ (`enableScripts: false` in `.yarnrc.yml`) | ✓ (`--ignore-scripts` flag; `ignoreScripts = true` in `bunfig.toml`) |
| Frozen lockfile | use `npm ci` | ✓ env var | `yarn install --frozen-lockfile` | `yarn install --immutable` | `bun install --frozen-lockfile` |
| Opt-in script allowlist | ✗ none | `onlyBuiltDependencies` (10.x) → `allowBuilds` (11.x) in `package.json` | ✗ | ✗ | `trustedDependencies` array in `package.json` |

**Strategic takeaway:**

- **pnpm projects** get all four protections; strongest posture.
- **npm projects** get three (`before` plus `ignore-scripts` plus `npm ci`).
- **yarn classic and yarn berry** have no rolling-window or date-pinned quarantine. Defense is limited to `ignore-scripts`, lockfile immutability, and external scanners (OSV-Scanner, Socket).
- **bun** has the clean `trustedDependencies` opt-in but no date-pinned install support. Rely on `ignore-scripts` and external scanners.

**Recommendation for new projects:** prefer pnpm specifically for its supply-chain hardening surface area.

## The Single Source-of-Truth Hardening Script

Create one file, `~/.npm-hardening.sh`, in POSIX shell syntax. Source it from every shell init that matters. The same file works on macOS, Linux, and WSL.

```sh
# ~/.npm-hardening.sh — POSIX sh; works in bash, zsh, dash, sh

# Rolling 7-day quarantine, recomputed at shell start.
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

The next several sections wire this file into each platform and shell.

## Setup: macOS

### zsh (macOS Default Since 10.15)

zsh on macOS reads `~/.zshenv` for every invocation: interactive, login, scripts, subshells. Adding the sourcer there gives universal coverage.

```sh
# Append to ~/.zshenv
[ -r "$HOME/.npm-hardening.sh" ] && . "$HOME/.npm-hardening.sh"
```

If your `~/.zshenv` already loops over a directory of `.zsh` files, drop a one-line file instead: `~/.zshenv.d/npm-hardening.zsh` containing the same source line.

### bash (Interactive)

```sh
# Append to ~/.bashrc
[ -r "$HOME/.npm-hardening.sh" ] && . "$HOME/.npm-hardening.sh"
```

### bash (Login)

macOS Terminal.app opens login shells by default. iTerm2, VSCode, and most agent terminals open non-login shells. Cover both by adding the sourcer to both `~/.bash_profile` (or `~/.profile`) and `~/.bashrc`.

```sh
# Append to ~/.bash_profile or ~/.profile (whichever exists; create if neither)
[ -r "$HOME/.npm-hardening.sh" ] && . "$HOME/.npm-hardening.sh"
```

### fish

```fish
# Append to ~/.config/fish/conf.d/npm-hardening.fish
set -gx NPM_CONFIG_BEFORE (date -u -v-7d '+%Y-%m-%dT%H:%M:%SZ')
set -gx NPM_CONFIG_MINIMUM_RELEASE_AGE 10080
set -gx NPM_CONFIG_IGNORE_SCRIPTS true
set -gx NPM_CONFIG_FROZEN_LOCKFILE true
```

fish does not source POSIX files cleanly, so reproduce the exports directly. Files under `~/.config/fish/conf.d/` are auto-sourced.

### Verification (Any Shell On macOS)

```sh
pnpm config get before                # ISO date roughly 7 days ago
pnpm config get minimum-release-age   # 10080
pnpm config get ignore-scripts        # true
pnpm config get frozen-lockfile       # true
npm config get before                 # JS Date string roughly 7 days ago
npm config get ignore-scripts         # true
```

`npm` will print "Unknown env config 'frozen-lockfile' / 'minimum-release-age'" warnings; those are pnpm-only features and npm still functions correctly.

## Setup: Linux (Debian/Ubuntu/Fedora/RHEL/Arch)

### bash (Interactive, Non-Login)

`~/.bashrc` is the workhorse on most distros and gets sourced by every interactive bash.

```sh
# Append to ~/.bashrc
[ -r "$HOME/.npm-hardening.sh" ] && . "$HOME/.npm-hardening.sh"
```

### bash (Login)

Useful for SSH sessions and terminal multiplexers that launch login shells.

```sh
# Append to ~/.bash_profile or ~/.profile (whichever exists)
[ -r "$HOME/.npm-hardening.sh" ] && . "$HOME/.npm-hardening.sh"
```

### zsh

```sh
# Append to ~/.zshenv
[ -r "$HOME/.npm-hardening.sh" ] && . "$HOME/.npm-hardening.sh"
```

### fish

Same recipe as macOS fish above.

### systemd User Environment (Linux-Specific)

The cleanest way to make the variables present in every process started by a user session, including non-interactive children launched by GUI applications or systemd user units, is `environment.d`:

```ini
# ~/.config/environment.d/npm-hardening.conf
NPM_CONFIG_MINIMUM_RELEASE_AGE=10080
NPM_CONFIG_IGNORE_SCRIPTS=true
NPM_CONFIG_FROZEN_LOCKFILE=true
NPM_CONFIG_BEFORE=2026-05-05T00:00:00Z
```

Caveat: `environment.d` files take static values. Refresh `BEFORE=` weekly via a systemd timer, a cron `@reboot` job that rewrites the file, or rely on shell-init recomputation for terminal-launched commands.

A simple timer to refresh weekly:

```ini
# ~/.config/systemd/user/npm-hardening-refresh.service
[Service]
Type=oneshot
ExecStart=/bin/sh -c 'sed -i "s|^NPM_CONFIG_BEFORE=.*|NPM_CONFIG_BEFORE=$(date -u -d \"7 days ago\" \"+%%Y-%%m-%%dT%%H:%%M:%%SZ\")|" %h/.config/environment.d/npm-hardening.conf'
```

```ini
# ~/.config/systemd/user/npm-hardening-refresh.timer
[Timer]
OnCalendar=daily
Persistent=true
[Install]
WantedBy=timers.target
```

Enable with `systemctl --user enable --now npm-hardening-refresh.timer`.

## Setup: Windows

### PowerShell 7 (pwsh)

Find your profile path with `$PROFILE` in PowerShell. Common location: `C:\Users\<you>\Documents\PowerShell\Microsoft.PowerShell_profile.ps1`. Create the file if it does not exist.

```powershell
# Append to $PROFILE
$env:NPM_CONFIG_BEFORE = (Get-Date).ToUniversalTime().AddDays(-7).ToString("yyyy-MM-ddTHH:mm:ssZ")
$env:NPM_CONFIG_MINIMUM_RELEASE_AGE = "10080"
$env:NPM_CONFIG_IGNORE_SCRIPTS = "true"
$env:NPM_CONFIG_FROZEN_LOCKFILE = "true"
```

### PowerShell 5 (Windows PowerShell)

Profile path: `C:\Users\<you>\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`. Same body as PS7.

### Persistent User-Wide (Survives Reboot, Visible To All Shells)

Setting the variables in the user's registry hive makes them visible to cmd, PowerShell, and any GUI-launched process the user starts:

```powershell
[Environment]::SetEnvironmentVariable("NPM_CONFIG_IGNORE_SCRIPTS", "true", "User")
[Environment]::SetEnvironmentVariable("NPM_CONFIG_MINIMUM_RELEASE_AGE", "10080", "User")
[Environment]::SetEnvironmentVariable("NPM_CONFIG_FROZEN_LOCKFILE", "true", "User")
[Environment]::SetEnvironmentVariable("NPM_CONFIG_BEFORE",
  (Get-Date).ToUniversalTime().AddDays(-7).ToString("yyyy-MM-ddTHH:mm:ssZ"), "User")
```

To refresh `BEFORE=` daily, schedule a task: **Task Scheduler → Create Basic Task → trigger Daily at 03:00 → action: `powershell.exe -Command`** with the `SetEnvironmentVariable` line above.

### cmd.exe

cmd is rarely used as a primary shell. If you need it, the persistent registry-based approach above is the only path; cmd has no init file equivalent to `.bashrc`. The `setx` command writes the same registry entries:

```cmd
setx NPM_CONFIG_IGNORE_SCRIPTS true
setx NPM_CONFIG_MINIMUM_RELEASE_AGE 10080
setx NPM_CONFIG_FROZEN_LOCKFILE true
```

Note: `setx` does not affect the current cmd session; open a new shell to pick up the values.

### Git Bash

Git Bash reads POSIX init files at `~/.bashrc` and `~/.bash_profile`. Drop the same `~/.npm-hardening.sh` into your Git Bash home directory (path resolves to something like `C:\Users\<you>\.npm-hardening.sh`), then add the sourcer line to `~/.bashrc`:

```sh
[ -r "$HOME/.npm-hardening.sh" ] && . "$HOME/.npm-hardening.sh"
```

### WSL (Ubuntu, Debian, Fedora Under Windows)

WSL behaves like Linux. Follow the Linux recipes above. The Windows-side environment variables do not automatically propagate into WSL by default; configure WSL's user environment independently.

## Setup: CI Runners

CI environments do not source user shell init. Inject the variables into the runner's environment explicitly.

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
```

### GitLab CI

```yaml
variables:
  NPM_CONFIG_IGNORE_SCRIPTS: "true"
  NPM_CONFIG_FROZEN_LOCKFILE: "true"
  NPM_CONFIG_MINIMUM_RELEASE_AGE: "10080"
before_script:
  - export NPM_CONFIG_BEFORE=$(date -u -d '7 days ago' '+%Y-%m-%dT%H:%M:%SZ')
```

### CircleCI, Buildkite, Jenkins

Same pattern: set the three static variables in the job environment, compute `NPM_CONFIG_BEFORE` in a pre-install step.

## Pinning Install Scripts (Opt-In Execution)

With `ignore-scripts=true`, some legitimate workflows need install hooks. Two clean patterns allow them per-package without disabling `ignore-scripts` globally.

### pnpm 10.x: `onlyBuiltDependencies` In `package.json`

```json
{
  "pnpm": {
    "onlyBuiltDependencies": ["esbuild", "lefthook", "sharp"]
  }
}
```

With `ignore-scripts=true` set globally, pnpm 10 still executes install scripts for packages on this allowlist. Deny by default, allow specific trusted names.

### pnpm 11.x: `allowBuilds`

```json
{
  "pnpm": {
    "allowBuilds": ["esbuild", "lefthook", "sharp"]
  }
}
```

Migration: rename the key when upgrading to pnpm 11.

### bun: `trustedDependencies`

```json
{
  "trustedDependencies": ["esbuild", "lefthook"]
}
```

### npm: No Per-Package Allowlist

npm has no equivalent. Either run with `--ignore-scripts` (block all) or without (allow all). Workaround: install with `--ignore-scripts`, then for specific packages you trust, run their postinstall manually (most expose a binary you can invoke explicitly, for example `lefthook install`).

## IOC Feeds

Use multiple feeds. Each has gaps; the union catches everything in practice.

### Tier 1: Free, Machine-Readable, Comprehensive

| Feed | Coverage | How To Consume | Update Lag |
| --- | --- | --- | --- |
| **OSV.dev** | All ecosystems including npm; malicious packages tagged with `MAL-*` IDs | REST: `POST https://api.osv.dev/v1/query`; bulk via `osv-scanner --download-offline-databases`; raw Git mirror at `github.com/google/osv.dev` | Minutes after upstream advisory |
| **GitHub Advisory Database (GHSA)** | Backs `npm audit`; npm plus several other ecosystems | `gh api graphql` for `securityAdvisories`; `npm audit` and `pnpm audit` for installed packages | Minutes; npm publishes here first |
| **deps.dev** (Google) | Dependency graph and vulnerability rollups | REST: `GET https://api.deps.dev/v3alpha/systems/npm/packages/<name>` | Same as OSV (shares data) |

### Tier 2: Free Public Feeds With Attack-Specific Reporting

| Feed | Coverage | How To Consume |
| --- | --- | --- |
| **Aikido Intel** | Live tracker; novel-attack writeups; affected-package lists for every named campaign | Web at `aikido.dev/intel`; CLI `npm install -g @aikidosec/safe-chain` |
| **StepSecurity Blog** | Frequently the first public detector (detected TanStack within 20 minutes); publishes IOC tables | RSS at `stepsecurity.io/blog/feed` |
| **Socket.dev Advisories** | Per-package risk scoring; novel-attack tracking; sandboxed package execution | Free tier: web UI plus `socket.dev/npm/package/<name>`; CLI `npm install -g socket` |
| **Datadog Security Labs** | Worm-pattern analysis; deep technical posts | Blog: `securitylabs.datadoghq.com` |
| **Wiz Threat Intel** | Pre-built queries; some content gated | `threats.wiz.io` |
| **Unit 42 (Palo Alto)** | "Monitoring npm supply chain attacks" living doc, kept current | `unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks` |
| **CISA Alerts** | US-CERT advisories for major incidents (Axios and Shai-Hulud got CISA writeups) | `cisa.gov/news-events/alerts` |

### Tier 3: Commercial (For SLAs Or Private-Package Coverage)

- **Snyk Vulnerability DB**: comprehensive; paid above small-team tier.
- **Phylum**: built around supply-chain-attack use case specifically.
- **JFrog Xray**: fits if you are already on Artifactory.
- **Sonatype OSS Index**: free public read-only API; paid for advanced features.

### Curated Single-File IOC Dumps (Community)

For specific named campaigns, individual researchers publish JSON lists of exact `package@version` pairs that can be grep'd against lockfiles directly:

- **Shai-Hulud 2.0**: `https://blog.ehsan.it/shai-hulud-v2-ioc.json` (community-maintained; cross-check with vendor lists).
- **TanStack (2026-05-11)**: see [tanstack.com postmortem](https://tanstack.com/blog/npm-supply-chain-compromise-postmortem) for the canonical 84-version list.

### Subscribe-And-Watch Playbook

1. Add the StepSecurity RSS and Aikido Intel pages to daily reading.
2. Run `osv-scanner` against every lockfile in CI on every PR.
3. Weekly: `gh api graphql -f query='query{securityAdvisories(ecosystem:NPM, publishedSince:"YYYY-MM-DD"){...}}'` piped to a Slack or email channel.

## Local Scanning Tools

The chain: snapshot what is installed, check against feeds, act.

### `osv-scanner` (Google, Free, Go Binary)

Recommended baseline. Install prebuilt binaries from `github.com/google/osv-scanner/releases` for macOS/Linux/Windows, or `go install github.com/google/osv-scanner/v2/cmd/osv-scanner@latest`.

```bash
# scan a single project
osv-scanner -L pnpm-lock.yaml
osv-scanner -L package-lock.json

# scan recursively from cwd
osv-scanner scan source -r .

# offline mode (download DB once, scan in air-gapped env)
osv-scanner --offline --download-offline-databases ./osvdb
```

Supports `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, plus 16+ other ecosystems. Output JSON with `--format json`.

### `npm audit` And `pnpm audit`

Backed by GHSA. Run after every lockfile change.

```bash
pnpm audit --audit-level=moderate
npm audit --audit-level=moderate
```

Caveat: surfaces vulnerabilities, not always *malicious* packages. The distinction matters. For pure supply-chain-attack detection, OSV is more direct.

### `socket` CLI

```bash
npm install -g socket
socket scan create .            # uploads manifest, returns risk report
socket npm install <pkg>        # wraps npm with pre-install supply-chain checks
```

Free tier covers public packages. Strong on novel-attack detection because Socket executes packages in a sandbox.

### `aikido safe-chain`

```bash
npm install -g @aikidosec/safe-chain
safe-chain npm install <pkg>    # wrapper similar to socket
```

Free, opinionated toward blocking obviously-suspicious packages at install time.

### `npq` (npm-Quarantine, Community)

```bash
npm install -g npq
npq install some-package
```

Wraps `npm install` with basic supply-chain checks first.

### Manual Lockfile Grep Against A Known-Bad List

When a brand-new IOC list drops and you do not want to wait for `osv-scanner` to ingest it, grep directly:

```bash
#!/usr/bin/env bash
# Usage: scan-iocs.sh /path/to/lockfile  ioc1@ver  ioc2@ver  ...
LOCK="$1"; shift
for ioc in "$@"; do
  pkg="${ioc%@*}"; ver="${ioc##*@}"
  case "$LOCK" in
    *pnpm-lock.yaml)
      grep -qE "['/]${pkg}@${ver}[:'(]" "$LOCK" && echo "HIT: $ioc" ;;
    *package-lock.json)
      grep -B1 "\"version\": \"${ver}\"" "$LOCK" \
        | grep -q "\"node_modules/${pkg}\"" && echo "HIT: $ioc" ;;
    *yarn.lock)
      grep -qE "^\"?${pkg}@${ver}\"?:" "$LOCK" && echo "HIT: $ioc" ;;
  esac
done
```

## Operational Checklist

### Initial Setup (Every Workstation)

- [ ] Create `~/.npm-hardening.sh` (or platform equivalent).
- [ ] Hook it from every shell init that matters: bash plus zsh, login plus non-login.
- [ ] Verify: `pnpm config get before`, `npm config get before`, `pnpm config get ignore-scripts`.
- [ ] Run `osv-scanner -r .` from each workspace root; investigate any hits.
- [ ] Rotate any plaintext `_authToken` in `~/.npmrc` to a read-only token (`npm token create --read-only`).

### Per-Project (When Adding Or Removing Dependencies)

- [ ] To intentionally install a fresh package, explicitly unset the quarantine variables per command, visibly:
      `NPM_CONFIG_BEFORE= NPM_CONFIG_MINIMUM_RELEASE_AGE=0 NPM_CONFIG_FROZEN_LOCKFILE=false pnpm add some-pkg`.
      Or use `--before=<known-safe-date>`.
- [ ] After lockfile change, run `osv-scanner -L <new lockfile>`.
- [ ] Commit lockfile.

### Weekly

- [ ] Skim Aikido Intel, StepSecurity, and Unit 42 living doc for new named attacks. Add their IOC lists to a local `known-bad.txt` if relevant.
- [ ] Refresh the rolling `NPM_CONFIG_BEFORE` (happens automatically on shell restart; long-lived tmux sessions need explicit reload).

### When A New Named Attack Drops

- [ ] Run the grep recipe against every lockfile in your workspace with that attack's IOC list.
- [ ] If you have hits: revoke every npm, GitHub, and cloud token reachable from any machine that ran `pnpm install` while the malicious version was live (typically the same day). Check `~/.npmrc`, `~/.gitconfig`, `~/.aws/credentials`, `~/.config/gh/` for traces.
- [ ] Pin to the last known-good version in `package.json`. Run `pnpm install --before=<date-of-known-good>`. Commit.
- [ ] Subscribe to the affected project's GitHub Security Advisories.

## Common Questions

**Does `before=` block legitimate security patches that landed in the last 7 days?**
Yes, by design. The trade-off: 7 days of delayed security patches versus zero days of supply-chain malware exposure. Historically the latter has been the bigger source of incidents for typical projects. For genuinely urgent CVEs (a 0-day RCE), opt out per command.

**How does this interact with Renovate or Dependabot?**
Both have native equivalents. Renovate supports `minimumReleaseAge: "7 days"` in `renovate.json`. Dependabot does not yet (as of 2026-05); track this. Renovate's filter is independent of pnpm's; both should be on.

**What about a private registry or npm Enterprise?**
Mirror to Verdaccio, Artifactory, or Nexus with a delay-replication policy (Artifactory has a "version-quarantine" feature). That moves the quarantine into the registry layer and protects the whole org at once. Out of scope here, but the strongest org-level posture.

**My CI runs `npm ci` (or `pnpm install --frozen-lockfile`). Am I safe?**
Only as safe as your lockfile. If a developer ran `pnpm add` on a fresh machine without the hardening, a malicious version is now baked into the committed lockfile, and CI happily installs it. Defense in depth: enforce hardening in CI too (set variables in the runner before `pnpm install`), and run `osv-scanner` against the lockfile in a separate CI job that blocks merge on findings.

**Does `ignore-scripts=true` break `npm install -g` for CLI tools?**
Some, including anything that uses postinstall to set up symlinks or download binaries. Pattern: install global CLI tools with `NPM_CONFIG_IGNORE_SCRIPTS=false npm install -g <vetted-tool>`; install everything else with the default.

## Updating This Document

This is a living document. The threat landscape changes on a weeks-to-months cadence; the protections (env-var pattern, IOC feeds, scanner tools) change on a months-to-years cadence. Maintain Part 2 (notable exploits) more aggressively than Parts 1 or 3.

Procedures, citation rules, and suggested agent prompts are in [`self-update-instructions.md`](self-update-instructions.md) → "Updating Research Docs".

---

## Sources

### Attack-Specific Writeups (2025-2026)

- [CISA: Widespread Supply Chain Compromise Impacting npm Ecosystem (Sep 23 2025)](https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem)
- [Unit 42: Shai-Hulud Worm Compromises npm Ecosystem (updated 2025-11-26)](https://unit42.paloaltonetworks.com/npm-supply-chain-attack/)
- [Unit 42: npm Threat Landscape, living doc updated 2026-05-01](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/)
- [StepSecurity: 20+ Popular NPM Packages Compromised (qix incident)](https://www.stepsecurity.io/blog/20-popular-npm-packages-compromised-chalk-debug-strip-ansi-color-convert-wrap-ansi)
- [Socket: npm Author Qix Compromised in Major Supply Chain Attack](https://socket.dev/blog/npm-author-qix-compromised-in-major-supply-chain-attack)
- [Sysdig: Shai-Hulud, the novel self-replicating worm infecting hundreds of NPM packages](https://www.sysdig.com/blog/shai-hulud-the-novel-self-replicating-worm-infecting-hundreds-of-npm-packages)
- [Datadog Security Labs: Shai-Hulud 2.0 npm worm analysis](https://securitylabs.datadoghq.com/articles/shai-hulud-2.0-npm-worm/)
- [Wiz: Sha1-Hulud 2.0 Supply Chain Attack, 25K+ Repos Exposed](https://www.wiz.io/blog/shai-hulud-2-0-ongoing-supply-chain-attack)
- [Netskope: Shai-Hulud 2.0, Aggressive, Automated, Fast Spreading](https://www.netskope.com/blog/shai-hulud-2-0-aggressive-automated-one-of-fastest-spreading-npm-supply-chain-attacks-ever-observed)
- [Microsoft Security: Mitigating the Axios npm supply chain compromise (Apr 1 2026)](https://www.microsoft.com/en-us/security/blog/2026/04/01/mitigating-the-axios-npm-supply-chain-compromise/)
- [Google Cloud / Mandiant: DPRK Threat Actor Compromises Axios](https://cloud.google.com/blog/topics/threat-intelligence/north-korea-threat-actor-targets-axios-npm-package)
- [CISA: Supply Chain Compromise Impacts Axios Node Package Manager (Apr 20 2026)](https://www.cisa.gov/news-events/alerts/2026/04/20/supply-chain-compromise-impacts-axios-node-package-manager)
- [The Hacker News: SAP-Related npm Packages Compromised (Apr 29 2026)](https://thehackernews.com/2026/04/sap-npm-packages-compromised-by-mini.html)
- [The Register: Ongoing supply chain attacks worm into SAP npm packages (Apr 30 2026)](https://www.theregister.com/2026/04/30/supply_chain_attacks_sap_npm_packages/)
- [TanStack Postmortem: npm supply-chain compromise (May 11 2026)](https://tanstack.com/blog/npm-supply-chain-compromise-postmortem)
- [StepSecurity: Mini Shai-Hulud Is Back, Self-Spreading Attack Hits npm](https://www.stepsecurity.io/blog/mini-shai-hulud-is-back-a-self-spreading-supply-chain-attack-hits-the-npm-ecosystem)
- [Aikido: Mini Shai-Hulud Is Back, npm Worm Hits 160+ Packages including Mistral and Tanstack](https://www.aikido.dev/blog/mini-shai-hulud-is-back-tanstack-compromised)
- [Wiz: Mini Shai-Hulud Strikes Again, TanStack + more npm Packages](https://www.wiz.io/blog/mini-shai-hulud-strikes-again-tanstack-more-npm-packages-compromised)
- [Snyk: TanStack npm Packages Hit by Mini Shai-Hulud](https://snyk.io/blog/tanstack-npm-packages-compromised/)
- [The Hacker News: Mini Shai-Hulud Worm Compromises TanStack, Mistral AI, Guardrails AI](https://thehackernews.com/2026/05/mini-shai-hulud-worm-compromises.html)
- [Socket: TanStack npm Packages Compromised in Mini Shai-Hulud](https://socket.dev/blog/tanstack-npm-packages-compromised-mini-shai-hulud-supply-chain-attack)
- [SafeDep: Mass Supply Chain Attack Hits TanStack, Mistral AI npm and PyPI Packages](https://safedep.io/mass-npm-supply-chain-attack-tanstack-mistral/)

### Tools And Feeds

- [OSV.dev, Open Source Vulnerabilities database](https://osv.dev/)
- [OSV-Scanner on GitHub](https://github.com/google/osv-scanner)
- [pnpm settings reference (`minimumReleaseAge`, `ignore-scripts`)](https://pnpm.io/settings)
- [npm config docs (precedence and env vars)](https://docs.npmjs.com/cli/v11/configuring-npm/npmrc)
- [Socket, supply-chain risk platform](https://socket.dev/)
- [Aikido Intel feed](https://www.aikido.dev/intel)
- [Snyk Vulnerability Database](https://snyk.io/vuln/)
- [GitHub Advisory Database](https://github.com/advisories?query=type%3Areviewed+ecosystem%3Anpm)
- [deps.dev API](https://deps.dev/)

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
