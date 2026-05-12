# PyPI Operational Hardening

**Last updated:** 2026-05-12

**Author:** Joshua Levy (github.com/jlevy) and LLM assistance

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
export UV_ONLY_BINARY=":all:"

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
  set -gx UV_ONLY_BINARY ":all:"
  set -gx PIP_UPLOADED_PRIOR_TO "P7D"
  ```
- **Windows PowerShell**: add to `$PROFILE` (see
  [research-pypi-supply-chain-hardening.md](../research/research-pypi-supply-chain-hardening.md#powershell-7-pwsh)).

### Step 3: Verify

```sh
uv pip install --dry-run requests 2>&1 | head -5   # should show exclude-newer in effect
pip config get global.only-binary                   # :all:
echo "$UV_EXCLUDE_NEWER"                            # 7 days
echo "$PIP_UPLOADED_PRIOR_TO"                       # P7D
```

### Step 4: When You Intentionally Need A Fresh Package

Unset the quarantine env vars per command, visibly:

```sh
UV_EXCLUDE_NEWER= UV_ONLY_BINARY= uv pip install some-pkg
PIP_UPLOADED_PRIOR_TO= PIP_ONLY_BINARY= pip install some-pkg
```

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

1. **Revoke every credential reachable** from any machine that ran `pip install`,
   `uv sync`, or `poetry install` while the malicious version was live.
   Cover: PyPI tokens, GitHub tokens (`~/.config/gh/`), cloud creds
   (`~/.aws/credentials`, `~/.config/gcloud/`), and any env-var-stored API keys.
2. **Pin to the last known-good version** in your requirements or lockfile.
   Regenerate the lockfile and commit.
3. **Inspect shell history and config files** for exfiltrated content or unexpected
   modifications.

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
  UV_ONLY_BINARY: ":all:"
  PIP_ONLY_BINARY: ":all:"
  PIP_UPLOADED_PRIOR_TO: "P7D"
jobs:
  install:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: uv sync --frozen
      - run: pip-audit
```

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
