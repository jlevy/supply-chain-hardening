# PyPI Operational Hardening

**Last updated:** 2026-08-04

**Author:** Joshua Levy (github.com/jlevy) with agent assistance

The minimum action list to harden a workstation or CI runner against PyPI supply-chain
attacks, and to check whether you have already been compromised.
Full threat model, per-platform setup, IOC feeds, and scanning tools in
[research-pypi-supply-chain-hardening.md](../research/research-pypi-supply-chain-hardening.md).

This guide is install-side.
If you *publish* to PyPI, the dominant 2026 vector is a stolen PyPI API token used from
CI (LiteLLM, `durabletask`): prefer PyPI Trusted Publishers (OIDC) over long-lived
tokens and follow [`hardening-ci-cd.md`](hardening-ci-cd.md).

> [!WARNING]
> **A wheel-only policy is a defence against source builds, not against code
> execution.** The June 2026 Hades campaign shipped `.pth` files *inside wheels*.
> Python’s `site` module executes any line in a `.pth` file that starts with `import`,
> at every interpreter startup, whether or not you ever import the package.
> `PIP_ONLY_BINARY`, `--no-build`, and `UV_NO_BUILD` do nothing about it.
> See [Step 5](#step-5-audit-pth-interpreter-startup-hooks).

## Hardening (Ten-Minute Setup)

### Step 1: Create the Hardening Script

Create `~/.pypi-hardening.sh` with the three protection env vars:

```sh
# Rolling 14-day install quarantine for uv.
# Friendly durations ("14 days") need a recent uv: supported on uv >= 0.9 (verified on
# 0.9.25 and 0.11.x), rejected by uv 0.8.x and earlier. Run a current uv (the cool-off
# window applies to your own toolchain too); only if you are pinned to an old uv, use an
# absolute date instead (export UV_EXCLUDE_NEWER=2026-05-13).
export UV_EXCLUDE_NEWER="14 days"

# Refuse third-party source distributions (sdists). Blocks setup.py code execution at
# install time. pip's --only-binary exempts your own local/editable project, so it is
# safe to export globally. (uv's UV_NO_BUILD is *not* safe to export globally—see the
# box below.)
export PIP_ONLY_BINARY=":all:"

# pip 26.1+ rolling quarantine. P14D = 14 days in ISO 8601 duration format.
export PIP_UPLOADED_PRIOR_TO="P14D"
```

> **Do not export `UV_NO_BUILD` globally—it breaks `uv sync`.** uv builds your project’s
> own (editable) package on every `uv sync`, so a blanket `UV_NO_BUILD=true` fails it:
> 
> ```
> error: Distribution `yourpkg==0.1.0 @ editable+.` can't be installed because it is
> marked as `--no-build` but has no binary distribution
> ```
> 
> Verified on uv 0.8.17 and 0.11.16. pip’s `--only-binary :all:` does **not** have this
> problem—it still builds your local project (verified on pip 26.1), which is why the
> recipe keeps it but drops `UV_NO_BUILD`. Apply uv’s no-build protection where it
> actually guards you—pulling in third-party tools and dependencies:
> 
> ```sh
> uv pip install --no-build <third-party-dep>   # refuse an sdist for this install
> uv tool install --no-build <tool>
> ```
> 
> For an always-on guard during `uv sync` without blocking your own build, deny-list the
> specific packages that must never build from source rather than reaching for the
> blanket flag:
> 
> ```sh
> export UV_NO_BUILD_PACKAGE="pkg-a pkg-b"      # uv refuses sdists only for these
> ```

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
  set -gx UV_EXCLUDE_NEWER "14 days"
  set -gx PIP_ONLY_BINARY ":all:"
  set -gx PIP_UPLOADED_PRIOR_TO "P14D"
  ```
- **Windows PowerShell**: add to `$PROFILE` (see
  [research-pypi-supply-chain-hardening.md](../research/research-pypi-supply-chain-hardening.md#powershell-7-pwsh)).

### Step 3: Verify

```sh
# Shell-state check: each variable is set in the current shell.
env | grep -E '^(UV_EXCLUDE_NEWER|PIP_ONLY_BINARY|PIP_UPLOADED_PRIOR_TO)='

# Behaviour check: uv must refuse a known sdist-only build when --no-build is applied.
# This dry-run must fail (proves the flag is honored). Use the flag here rather than a
# global export, which would break `uv sync` in project directories.
uv pip install --no-build --dry-run --no-deps 'pyahocorasick==2.0.0' 2>&1 | head -5
```

Note: `pip config get global.only-binary` reads pip’s config files, not env vars; it
returns nothing if the value comes only from `PIP_ONLY_BINARY`. Use `env | grep` to
confirm env-var state, then a behaviour check to confirm the process honors it.

Env-var-only setups are not visible to GUI-launched agents or non-interactive
subprocesses that do not inherit your shell environment.
If you run agents through a desktop launcher, also configure the system-wide environment
(see `research/research-pypi-supply-chain-hardening.md` → “systemd User Environment” or
the macOS launchd / Windows User-wide instructions).

### Step 4: When You Intentionally Need a Fresh Package

As with npm, the age gate (`UV_EXCLUDE_NEWER` / `PIP_UPLOADED_PRIOR_TO`) applies at
resolution time, so prefer a surgical, hash-pinned install over relaxing the gate.
A fresh-version exception (e.g. an urgent CVE patch) needs only a wheel; it does **not**
need source-build execution, so keep the sdist / no-build protection in place
throughout.

#### Verify First

PyPI has no `npm view` equivalent; query the JSON API for the exact version’s upload
time and per-file digests:

```sh
curl -s https://pypi.org/pypi/<pkg>/<version>/json \
  | jq -r '.urls[] | "\(.filename)\t\(.upload_time_iso_8601)\t\(.digests.sha256)\t\(.url)"'
```

No `jq`? The same fields are plain JSON: `urls[].filename`,
`urls[].upload_time_iso_8601`, `urls[].digests.sha256`, `urls[].url`. Confirm the upload
time matches the release you intend, then keep the wheel’s `sha256` and `url` for the
next step.

#### Surgical Install (Preferred)

Install the specific wheel by URL with its hash.
pip verifies the `#sha256` fragment against the downloaded file and never re-resolves
the version through the gate:

```sh
# pip verifies the fragment hash:
pip install "https://files.pythonhosted.org/.../<pkg>-<version>-py3-none-any.whl#sha256=<sha256>"
# uv:
uv pip install "https://files.pythonhosted.org/.../<pkg>-<version>-py3-none-any.whl"
```

This bypasses the age gate for one vetted wheel only, keeps sdist / no-build enforcement
intact, and cannot linger in your shell.

#### Exempt One Package, Not the Whole Graph (uv)

uv can carve out a single package rather than dropping the gate everywhere.
`exclude-newer-package` maps package names to their own cut-off, and `false` exempts a
package from the global `exclude-newer` entirely.
Prefer this over unsetting `UV_EXCLUDE_NEWER`, because the rest of the dependency graph
stays quarantined and the exemption is committed and reviewable rather than living in a
shell:

```toml
# pyproject.toml or uv.toml. The exemption is visible in code review.
[tool.uv]
exclude-newer = "14 days"
exclude-newer-package = { some-cve-patched-pkg = false }
```

The equivalent flag is `--exclude-newer-package <package>=false`, and the environment
variable is `UV_EXCLUDE_NEWER_PACKAGE`. Values take the same three forms as
`exclude-newer`: an RFC 3339 timestamp (`2026-08-01T00:00:00Z`), a friendly duration
(`14 days`), or an ISO 8601 duration (`P14D`). Remove the entry once the package ages
past the window; leaving it behind converts a one-off exception into a permanent hole.

#### Relax the Gate (Last Resort)

Only when you cannot construct a wheel URL and are not on uv.
Unset **only the age gate** inline, keeping sdist / no-build enforcement:

```sh
# Fresh wheel only: bypass the age gate, keep no-build / wheel-only enforcement.
UV_EXCLUDE_NEWER= uv pip install <pkg>==<version>
PIP_UPLOADED_PRIOR_TO= pip install <pkg>==<version>
```

Only if a package genuinely has no wheel and must be built from source, take the
separate, louder build exception (review the `setup.py` / `build` first, ideally in a
sandbox):

```sh
# Source build exception: scope it narrowly and review the build code first.
UV_NO_BUILD= uv pip install some-sdist-only-pkg
PIP_ONLY_BINARY= pip install some-sdist-only-pkg
```

#### Verify-Then-Install Checklist

Every exception ends in the [exception process](../README.md#the-exception-process):

1. **Verify:** query the JSON API; confirm the upload time and record the wheel
   `sha256`.
2. **Install surgically:** wheel URL with `#sha256=`; keep sdist / no-build on.
3. **Record:** log the exception in `supply-chain-audit-log.md` with the reason (a CVE
   ID for security patches), the exact `pkg==version`, and the verified `sha256`.

### Step 5: Audit `.pth` Interpreter Startup Hooks

Python’s `site` module reads every `.pth` file in `site-packages` at interpreter startup
and **executes any line beginning with `import`**. The feature exists so that packaging
tools can install import hooks; the June 2026 Hades campaign used it to run a credential
stealer on every `python` invocation.

Why the rest of this playbook does not cover it:

| Control | Why it misses `.pth` |
| --- | --- |
| `PIP_ONLY_BINARY` / `UV_NO_BUILD` | The hook ships **inside the wheel**. No source build happens. |
| Cool-off window | Works normally, and is the only Step 1 control that does apply. It is what bought detection time in the Hades case. |
| “Only import trusted packages” | Nothing is imported. Installation alone is enough. |
| Removing the package from your imports | The file stays in `site-packages` until the package is uninstalled. |

A legitimate `.pth` file contains only directory paths.
Two `import` lines are normal in practice: `distutils-precedence.pth` from setuptools,
and `__editable__.*.pth` from PEP 660 editable installs.
Treat anything else that executes as suspect.

```sh
# List every .pth file that executes code, across all site-packages of the active
# interpreter. Review each hit against the two known-good names above.
python3 - <<'PY'
import pathlib, site
dirs = [pathlib.Path(p) for p in (*site.getsitepackages(), site.getusersitepackages())]
for d in dirs:
    if not d.is_dir():
        continue
    for f in sorted(d.rglob("*.pth")):
        lines = [l for l in f.read_text(errors="replace").splitlines()
                 if l.strip().startswith("import")]
        if lines:
            print(f"{f}\n    {lines[0][:160]}")
PY
```

The repo’s scanner does the same check with the allow-list applied, across a project and
optionally the active interpreter:

```sh
uv run scripts/audit_workspace.py --only pth --scan-site-packages .
```

Run it once per virtualenv you care about; `.pth` files are per-environment, so a clean
result in one `.venv` says nothing about another.

### Notes and Caveats

- `UV_EXCLUDE_NEWER="14 days"` and `PIP_UPLOADED_PRIOR_TO="P14D"` are **not**
  syntactically interchangeable.
  uv accepts friendly durations on uv >= 0.9 (verified on 0.9.25 and 0.11.16); uv 0.8.x
  and earlier reject them, so run a current uv or use an absolute `YYYY-MM-DD` date
  there. pip 26.1+ accepts ISO 8601 durations (`P14D` = 14 days); setting
  `PIP_UPLOADED_PRIOR_TO=14 days` will silently fail to parse.
- **Run a current uv; the toolchain itself is a control.** uv 0.12 (2026-07-28) rejects
  MD5-only hashes in hash-checking mode, rejects wheels that could overwrite the Python
  interpreter (including case variants and data-directory installs), rejects
  distributions whose metadata name does not match the file, and rejects PEP 517 backend
  paths that escape the source tree through symlinks.
  Those are supply-chain checks you do not get by configuration, only by upgrading.
  The cool-off applies to your own toolchain too, so take uv upgrades on the same 14-day
  terms as anything else.
- **The cool-off covers the whole resolved set, not just the package you named.** Adding
  or upgrading one dependency can pull in many transitive packages, any of which may be
  brand-new. Review the full `uv.lock` / lockfile diff and confirm the cool-off for
  *every* newly-added package, not only the direct one.
  To fix a single violator without re-resolving the whole graph, pin it forward in
  place:
  ```sh
  uv lock --upgrade-package <name>==<version>   # bump only this package in the lock
  ```
- **Run scanners as isolated, pinned tools—never as project dependencies.** Adding
  `pip-audit` (or any scanner) to `[dependency-groups]` / `dev` drags its ~20 transitive
  packages into your `uv.lock`, putting the scanner’s own tree under the cool-off and
  audit surface you are trying to keep small (and those transitive deps are themselves
  often days-old). Export the locked set and scan it with a pinned `uvx` tool instead:
  ```sh
  uv export --frozen --no-emit-project --all-extras --format requirements.txt > /tmp/reqs.txt
  uvx --from "pip-audit==<pinned-version>" pip-audit -r /tmp/reqs.txt
  ```
- `PIP_UPLOADED_PRIOR_TO` depends on the index serving upload-timestamp metadata.
  Public PyPI does; some private indexes (Artifactory, Nexus) may not.
  Verify with `pip install --dry-run --uploaded-prior-to P14D <pkg-from-private-index>`
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

### Step 1: Scan Every Lockfile and Environment

```sh
# Install once: https://github.com/google/osv-scanner/releases
osv-scanner scan source -L requirements.txt
osv-scanner scan source -L uv.lock
osv-scanner scan source -L poetry.lock
osv-scanner scan source -L pdm.lock

# Or scan the active virtual environment:
pip-audit
```

### Step 2: Grep For Known IOCs From the Most Recent Named Attacks

The most relevant PyPI attacks as of 2026-08-04. The cross-ecosystem table is in
[`compromised-packages.md`](../compromised-packages.md); this is the PyPI quick-grep
extract:

| Date | Name | Quick IOC Pattern |
| --- | --- | --- |
| 2026-06-08 | Hades | `embiggen==0.11.97`, `ensmallen==0.8.101`, `gpsea==0.9.14`, `pyphetools==0.9.120`, `phenopacket-store-toolkit==0.1.7`, `ppkt2synergy==0.1.1`, `langchain-core-mcp==1.4.2`/`1.4.3`, `openai-mcp==2.41.1`/`2.41.2`, `instructor-mcp==1.15.2`/`1.15.3`, `tiktoken-mcp==0.13.1`/`0.13.2`, `ray-mcp-server==0.2.1`. On-disk: any `*-setup.pth` in site-packages, plus `_index.js` |
| 2026-05-19 | TrapDoor | `cryptowallet-safety`, `defi-risk-scanner`, `eth-security-auditor`, `solidity-build-guard`, `env-loader-cli`, `git-config-sync`, `data-pipeline-check`. Fires at import, not install |
| 2026-05-19 | durabletask / TeamPCP Wave 4 | `durabletask==1.4.1`, `durabletask==1.4.2`, `durabletask==1.4.3` (clean `1.4.0`) |
| 2026-05-11 | TanStack cross-ecosystem | `mistralai==2.4.6`, `guardrails-ai==0.10.1` |
| 2026-04-30 | PyTorch Lightning | `pytorch-lightning==2.6.2`, `pytorch-lightning==2.6.3` (clean `2.6.1`) |
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
3. **Remove revocation-triggered persistence, then rotate.** Campaigns in the Shai-Hulud
   lineage install watchers that react to a stolen token being revoked; the 2026-08-04
   keyv worm `eval`s an operator-supplied handler on the first HTTP 4xx. Run
   `python3 scripts/audit_workspace.py --only host .` before touching credentials.
   Then **revoke** by category, from a different clean machine: PyPI publish tokens
   (PyPI account → API tokens); GitHub PAT/OAuth (`~/.config/gh`); cloud
   (`~/.aws/credentials`, `~/.config/gcloud/`, Azure CLI); Vault and Kubernetes tokens;
   SSH (`~/.ssh/*`); env-var-stored API keys, the dominant exfil target for the
   2022-2026 PyPI wave.
4. **Check persistence mechanisms specific to this payload.** `.pth` startup hooks are
   the PyPI-specific one and outlive an uninstall of the *importing* code: LiteLLM
   1.82.8 shipped `litellm_init.pth`, and the June 2026 Hades wheels shipped
   `*-setup.pth`. Run the audit in [Step 5](#step-5-audit-pth-interpreter-startup-hooks)
   against **every** virtualenv, not just the active one.
   Also check `systemctl --user list-unit-files --state=enabled` (LiteLLM added a
   systemd backdoor), running processes and CPU history (Ultralytics installed an XMRig
   miner), and the repository itself for planted `.claude/` or `.vscode/` autostart
   config ([`hardening-agent-workspaces.md`](hardening-agent-workspaces.md)).
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

## Keeping a Supply Chain Audit Log

Follow the same audit-log discipline described in
[hardening-npm.md](hardening-npm.md#keeping-a-supply-chain-audit-log).
Start from the [template](../supply-chain-audit-log-template.md) in this repository.

## CI Enforcement

CI environments do not source user shell init.
Inject the variables explicitly.

### GitHub Actions

```yaml
env:
  UV_EXCLUDE_NEWER: "14 days"      # friendly duration needs uv >= 0.9 (pinned below)
  PIP_ONLY_BINARY: ":all:"
  PIP_UPLOADED_PRIOR_TO: "P14D"
  UV_VERSION: "0.12.1"             # pin a recent uv; verify against pypi.org/project/uv/
  PIP_AUDIT_VERSION: "2.10.1"      # pin; verify against pypi.org/project/pip-audit/
jobs:
  install:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v8
        with:
          version: ${{ env.UV_VERSION }}
      # No global UV_NO_BUILD: `uv sync` builds this project's own package, and a blanket
      # no-build would fail it. The frozen lockfile is the gate here; vet sdist-only
      # third-party deps at add/upgrade time (uv pip install --no-build) instead.
      - run: uv sync --frozen
      - run: uv tool install --from "pip-audit==${PIP_AUDIT_VERSION}" pip-audit
      - run: pip-audit
```

**Note on scanner pinning.** The recipe pins both uv and `pip-audit` rather than pulling
the latest at job time, and runs the scanner as an isolated `uv tool` rather than a
project dependency (see Notes And Caveats).
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

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
