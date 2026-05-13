# PyPI Operational Hardening

**Last updated:** 2026-05-12

**Author:** Joshua Levy (github.com/jlevy) with agent assistance

The minimum action list to harden a workstation or CI runner against PyPI supply-chain
attacks, and to check whether you have already been compromised.
Full threat model, per-platform setup, IOC feeds, and scanning tools in
[research-pypi-supply-chain-hardening.md](../research/research-pypi-supply-chain-hardening.md).

## Hardening (Ten-Minute Setup)

### Step 1: Create The Hardening Script

Create `~/.pypi-hardening.sh` with the three protection env vars:

```sh
# Rolling 7-day install quarantine for uv.
# Accepts friendly durations natively; no date arithmetic needed.
export UV_EXCLUDE_NEWER="7 days"

# Refuse source distributions (sdists). Blocks setup.py code execution at install time.
export PIP_ONLY_BINARY=":all:"
export UV_NO_BUILD=true

# pip 26.1+ rolling quarantine. P7D = 7 days in ISO 8601 duration format.
export PIP_UPLOADED_PRIOR_TO="P7D"
```

### Step 2: Source From Shell Init

Pick the line for every shell you use.
Detail on each in
[research-pypi-supply-chain-hardening.md](../research/research-pypi-supply-chain-hardening.md#part-3-best-practices-for-hardening).

- **zsh** (any OS): add to `~/.zshenv`
  `[ -r "$HOME/.pypi-hardening.sh" ] && . "$HOME/.pypi-hardening.sh"`
- **bash, interactive** (any OS): add the same line to `~/.bashrc`.
- **bash, login** (macOS Terminal default, SSH sessions): add the same line to
  `~/.bash_profile` or `~/.profile`.
- **fish**: add to `~/.config/fish/conf.d/pypi-hardening.fish`:
  ```fish
  set -gx UV_EXCLUDE_NEWER "7 days"
  set -gx PIP_ONLY_BINARY ":all:"
  set -gx UV_NO_BUILD true
  set -gx PIP_UPLOADED_PRIOR_TO "P7D"
  ```
- **Windows PowerShell**: add to `$PROFILE` (see
  [research-pypi-supply-chain-hardening.md](../research/research-pypi-supply-chain-hardening.md#powershell-7-pwsh)).

### Step 3: Verify

```sh
# Shell-state check: each variable is set in the current shell.
env | grep -E '^(UV_EXCLUDE_NEWER|UV_NO_BUILD|PIP_ONLY_BINARY|PIP_UPLOADED_PRIOR_TO)='

# Behaviour check: uv should refuse a known sdist-only build under UV_NO_BUILD.
# This dry-run must fail when the env var is honored.
uv pip install --dry-run --no-deps 'pyahocorasick==2.0.0' 2>&1 | head -5
```

Note: `pip config get global.only-binary` reads pip’s config files, not env vars; it
returns nothing if the value comes only from `PIP_ONLY_BINARY`. Use `env | grep` to
confirm env-var state, then a behaviour check to confirm the process honors it.

Env-var-only setups are not visible to GUI-launched agents or non-interactive
subprocesses that do not inherit your shell environment.
If you run agents through a desktop launcher, also configure the system-wide environment
(see `research/research-pypi-supply-chain-hardening.md` → “systemd User Environment” or
the macOS launchd / Windows User-wide instructions).

### Step 4: When You Intentionally Need A Fresh Package

Unset the quarantine env vars per command, visibly:

```sh
UV_EXCLUDE_NEWER= UV_NO_BUILD= uv pip install some-pkg
PIP_UPLOADED_PRIOR_TO= PIP_ONLY_BINARY= pip install some-pkg
```

### Notes And Caveats

- `UV_EXCLUDE_NEWER="7 days"` and `PIP_UPLOADED_PRIOR_TO="P7D"` are **not**
  syntactically interchangeable.
  uv accepts friendly durations natively; pip 26.1+ accepts ISO 8601 durations (`P7D` =
  7 days). Setting `PIP_UPLOADED_PRIOR_TO=7 days` will silently fail to parse.
- `PIP_UPLOADED_PRIOR_TO` depends on the index serving upload-timestamp metadata.
  Public PyPI does; some private indexes (Artifactory, Nexus) may not.
  Verify with `pip install --dry-run --uploaded-prior-to P7D <pkg-from-private-index>`
  before trusting the control on a private index.
- For private packages, do **not** use `--extra-index-url` (or `PIP_EXTRA_INDEX_URL`).
  pip resolves across all indexes and the highest version wins, which is the
  dependency-confusion vector that hit PyTorch / torchtriton.
  Use a single index that routes to both public and private (e.g. through a proxy that
  prefers private over public for matching names), or scope private packages to a
  separate index URL via `--index-url` with explicit per-package routing.

### Agent Ban List

Do not run `uvx <pkg>` without an explicit version pin and a review of the resolved
`pkg==version`. Pinning: `uvx --from <pkg>==<exact-version> <cmd>`. Full agent rules are
in [`../AGENTS.md`](../AGENTS.md) → “Safety Rule For Agents”.
For untrusted first-runs, see
[`untrusted-repo-first-run.md`](untrusted-repo-first-run.md).

## Compromise Assessment

### Step 1: Scan Every Lockfile And Environment

```sh
# Install once: https://github.com/google/osv-scanner/releases
osv-scanner scan source -L requirements.txt
osv-scanner scan source -L uv.lock
osv-scanner scan source -L poetry.lock
osv-scanner scan source -L pdm.lock

# Or scan the active virtual environment:
pip-audit
```

### Step 2: Grep For Known IOCs From The Most Recent Named Attacks

The most relevant PyPI attacks as of 2026-05-12. The cross-ecosystem table is in
[`compromised-packages.md`](../compromised-packages.md); this is the PyPI quick-grep
extract:

| Date | Name | Quick IOC Pattern |
| --- | --- | --- |
| 2026-05-11 | TanStack cross-ecosystem | `mistralai==2.4.6`, `guardrails-ai==0.10.1` |
| 2026-03-24 | LiteLLM / TeamPCP | `litellm==1.82.7`, `litellm==1.82.8` |
| 2024-12-04 | Ultralytics | `ultralytics==8.3.41`, `8.3.42`, `8.3.45`, `8.3.46` |
| 2022-12-25 | PyTorch torchtriton | `torchtriton==2.0.0` (nightly builds only) |
| 2022-05-14 | ctx account takeover | `ctx` versions published 2022-05-14 through 2022-05-24 |

Quick grep template:

```sh
#!/usr/bin/env bash
# Usage: scan-pypi-iocs.sh /path/to/requirements-or-lockfile  ioc1==ver  ioc2==ver ...
FILE="$1"; shift
for ioc in "$@"; do
  pkg="${ioc%%==*}"; ver="${ioc##*==}"
  grep -qiE "${pkg}[= ]+${ver}" "$FILE" && echo "HIT: $ioc"
done
```

### Step 3: If You Have Hits

Follow the eight steps in order.
The same outline appears in every per-ecosystem playbook so that incident response stays
consistent regardless of which registry was hit.

1. **Identify scope.** Affected machine(s), exact command(s), and time window when the
   malicious version was installed (or imported, for runtime payloads like LiteLLM
   1.82.8’s `litellm_init.pth`). Get this before any cleanup.
2. **Preserve evidence before cleanup.** Snapshot the env(s):
   `pip freeze > /tmp/audit-snapshot-pip-$(date +%s).txt`, save `~/.pypirc`,
   `~/.bash_history`, virtualenv contents (`cp -a .venv /tmp/audit-snapshot-venv-...`),
   and any active scanner output.
   Commit into the private audit log before mutating.
3. **Rotate tokens by category.** PyPI publish tokens (PyPI account → API tokens);
   GitHub PAT/OAuth (`~/.config/gh`); cloud (`~/.aws/credentials`, `~/.config/gcloud/`,
   Azure CLI); SSH (`~/.ssh/*`); env-var-stored API keys (the dominant exfil target for
   the 2022-2026 PyPI wave).
4. **Check persistence mechanisms specific to this payload.** LiteLLM 1.82.8 added a
   systemd backdoor and a `.pth` file that runs at every Python startup; check
   `systemctl --user list-unit-files --state=enabled` and grep for `*.pth` under your
   site-packages. Ultralytics installed an XMRig miner; check running processes and CPU
   usage history.
5. **Remove or downgrade the affected dependency.** Pin to the last known-good version
   in `pyproject.toml` / `requirements.txt` / `uv.lock`.
6. **Regenerate lockfile from trusted sources.** `uv lock` (or
   `pip-compile --generate-hashes`) against the cool-off window in effect.
   Commit.
7. **Re-run the scanner to confirm clean.** `osv-scanner scan source -L uv.lock` and
   `pip-audit`. Treat any remaining `[MALICIOUS]` advisory as a failed cleanup.
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
  UV_EXCLUDE_NEWER: "7 days"
  UV_NO_BUILD: "true"
  PIP_ONLY_BINARY: ":all:"
  PIP_UPLOADED_PRIOR_TO: "P7D"
  PIP_AUDIT_VERSION: "2.9.0"   # pin; verify against pypi.org/project/pip-audit/
jobs:
  install:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: uv sync --frozen
      - run: uv tool install --from "pip-audit==${PIP_AUDIT_VERSION}" pip-audit
      - run: pip-audit
```

**Note on scanner pinning.** The recipe pins `pip-audit` rather than installing the
latest from PyPI at job time.
For production CI, pre-install pinned scanners into the runner image so the audit
pipeline does not itself depend on a fresh network fetch.

Other CI: see
[research-pypi-supply-chain-hardening.md](../research/research-pypi-supply-chain-hardening.md#setup-ci-runners)
for GitLab, CircleCI, Buildkite, Jenkins.

## Subscribe-And-Watch Feeds

For early warning of new named attacks:

- [PyPI Blog (incident reports)](https://blog.pypi.org/)
- [Aikido Intel](https://intel.aikido.dev)
- [StepSecurity Blog](https://www.stepsecurity.io/blog) (often the first public
  detector)
- [Socket.dev](https://socket.dev/)
- [Datadog Security Labs](https://securitylabs.datadoghq.com/)

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
