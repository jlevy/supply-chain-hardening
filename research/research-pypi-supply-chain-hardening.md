# PyPI Supply Chain Hardening

**Last updated:** 2026-05-23

**Author:** Joshua Levy (github.com/jlevy) with agent assistance

A working guide for locking down `pip`, `uv`, `pipx`, `poetry`, `pdm`, and
`conda`/`mamba` on developer workstations and CI runners against the 2022-2026
supply-chain attack wave targeting PyPI. Includes concrete configuration recipes,
per-platform and per-shell setup, indicator-of-compromise (IOC) feeds, and local
scanning tools.

The doc has three parts:

1. **Background**: why this matters and the pattern these attacks share.
2. **Notable Exploits**: the named incidents from 2022 through May 2026, with affected
   packages and dates so you can spot-check installed environments.
3. **Best Practices for Hardening**: copy-pasteable configuration for every major Python
   package manager, broken out by platform and shell.

A self-update section at the end describes when to refresh content and which
authoritative sources to verify against.

## Scope

**In scope:** developer-workstation and CI-runner hardening for the PyPI ecosystem.
Configuration of `pip` (>=26.1), `uv` (Astral, Rust-based), `pipx` (global tool
installs), `poetry`, `pdm`, and `conda`/`mamba`. IOC feeds and local scanners.
Cross-platform: macOS, Linux (Debian/Ubuntu/RHEL family), Windows (PowerShell, cmd, Git
Bash, WSL).

**Out of scope:** private PyPI mirrors (Artifactory, devpi, Nexus).
Container image scanning.
Runtime SBOM tracking.
GitHub Actions `pull_request_target` mitigation (referenced briefly in attack-mechanism
context only).

* * *

# Part 1: Background

The PyPI ecosystem has seen a steady drumbeat of supply-chain attacks since at least
2022, ranging from account takeovers of dormant packages to dependency-confusion attacks
against major ML frameworks, and culminating in the cross-ecosystem worm propagation of
May 2026. The attack surface differs from npm in important ways: Python’s `setup.py`
build system allows arbitrary code execution during `pip install` of source
distributions (sdists), and Python has historically lacked the lockfile-and-hash-pinning
culture that npm’s `package-lock.json` provides.

## What The Attacks Have In Common

Across the named incidents in this document, the playbook collapses to four primitives:

1. **Account takeover of a package maintainer.** Expired-domain re-registration (ctx,
   2022), stolen PyPI credentials via compromised CI/CD tooling (LiteLLM, 2026), or
   cross-ecosystem token theft from a compromised npm pipeline (mistralai,
   guardrails-ai, 2026).
2. **Publication of malicious versions to packages the victim owns.** Frequently
   high-download libraries (LiteLLM at ~95M monthly downloads, Ultralytics at ~60M
   downloads, mistralai SDK).
3. **Credential exfiltration or cryptominer deployment.** Most PyPI attacks exfiltrate
   environment variables (`os.environ`), AWS/GCP/Azure credentials, SSH keys, and shell
   history. The Ultralytics attack deployed an XMRig cryptocurrency miner instead.
4. **Dependency confusion.** Registering a public PyPI package with the same name as a
   private/internal dependency (torchtriton, 2022). pip’s default index precedence
   installs the higher-versioned public package over the intended private one.

**Common lifetime:** malicious versions live for minutes to hours before researchers
detect them and the package is yanked or quarantined by PyPI. A 7-day rolling quarantine
is effective: by the time a quarantined version becomes old enough to install, every
named incident below has already been remediated.

## Why Standard Practices Are Not Enough

- **`pip-audit` and `safety`** rely on vulnerability databases populated *after*
  malicious versions are detected.
  They tell you what to remove, not what to never install in the first place.
- **`requirements.txt` with pinned versions** locks to an exact version, including a
  malicious one if it was the latest when `pip install` ran.
- **`--only-binary :all:` alone** blocks sdist-based attacks (setup.py execution) but
  does nothing against malicious wheel payloads that execute on import (mistralai,
  LiteLLM). The full pattern needs multiple controls.
- **`pip install` without `--require-hashes`** does not verify package integrity.
  A compromised registry or man-in-the-middle can serve a different artifact than the
  one the maintainer uploaded.
- **For uv, project-local configuration** (`pyproject.toml [tool.uv]`, `uv.toml`) can
  override user-level settings.
  Environment variables beat project-local uv config; only an explicit CLI flag beats
  the env var.
- **For pip, project-local files like `pyproject.toml` and `setup.cfg` are not read as
  pip configuration.** Pip configuration comes from global / user / site `pip.conf` (or
  `pip.ini`), `PIP_CONFIG_FILE` if set, `PIP_*` environment variables, and CLI flags.
  Setting `[tool.pip]` in `pyproject.toml` has no effect on pip install behavior.
  (`pyproject.toml` does influence build-backend selection and dependency declarations,
  but that is build-system configuration, not pip configuration.)

## How PyPI Differs From npm

Several differences affect hardening strategy:

- **No install-time lifecycle hooks by default for wheels.** npm runs `postinstall`
  scripts automatically; pip does not run arbitrary code when installing a wheel.
  But sdists execute `setup.py`, and malicious payloads in wheels can trigger on
  `import`.
- **No native worm propagation mechanism.** npm’s `publish` token plus `postinstall`
  creates a worm vector.
  PyPI attacks have historically required a separate credential theft step, until the
  May 2026 cross-ecosystem propagation showed that npm worms can pivot to PyPI via
  stolen CI/CD tokens.
- **Weaker lockfile culture.** `requirements.txt` files often lack hashes.
  `uv.lock` and `poetry.lock` include hashes by default, which is a strong argument for
  adopting them.
- **Trusted Publishers and Sigstore attestations.** PyPI’s attestation system (GA since
  November 2024) provides cryptographic provenance that npm lacks.
  Projects using Trusted Publishing with the canonical GitHub Action produce Sigstore
  attestations by default.

* * *

# Part 2: Notable Exploits To Be Aware Of

The canonical cross-ecosystem table of named supply-chain incidents lives in
[`compromised-packages.md`](../compromised-packages.md).
Filter to `Ecosystem = PyPI` for the rows relevant to this guide.
New rows go there first; this section does not duplicate them.

**Reading the table:** if any `package==version` listed there appears in a lockfile or
installed environment, you almost certainly need to (1) rotate every credential
reachable from any machine that ran `pip install` while the malicious version was live,
and (2) downgrade to the immediately-prior version.

**Trend line:** PyPI attacks have been less frequent than npm but are accelerating.
The May 2026 cross-ecosystem propagation from the TanStack npm worm to PyPI marks a new
phase where npm and PyPI hardening are no longer independent concerns.
The dominant recent vector is a **stolen PyPI publish token used from CI**: TeamPCP
(LiteLLM, then `durabletask` on 2026-05-19) and the Mini Shai-Hulud wave
(`pytorch-lightning`, `mistralai`, `guardrails-ai`) all uploaded trojanized builds
directly via the API with no matching source-control tags or CI runs.
Publish-side controls (OIDC trusted publishing, scoped/expiring tokens) are now as
important as the install-side quarantine; see
[`../guidelines/hardening-ci-cd.md`](../guidelines/hardening-ci-cd.md).

## ctx Account Takeover (May 2022)

The `ctx` package (a small utility for dot-notation dictionary access) had not been
updated since December 2014. On May 14, 2022, a researcher purchased the expired domain
associated with the maintainer’s email address for $5, used PyPI’s password-reset flow
to take over the account, and published malicious versions that exfiltrated all
environment variables (`os.environ`) to a Heroku endpoint.

**Affected versions:** all `ctx` versions published between 2022-05-14 and 2022-05-24
(approximately 27,000 downloads in that window).

**Vector:** expired-domain account takeover, environment-variable exfiltration.

**Sources:**
[The Hacker News](https://thehackernews.com/2022/05/pypi-package-ctx-and-php-library-phpass.html);
[Sonatype](https://www.sonatype.com/blog/pypi-package-ctx-compromised-are-you-at-risk);
[BleepingComputer](https://www.bleepingcomputer.com/news/security/popular-python-and-php-libraries-hijacked-to-steal-aws-keys/);
[The Register](https://www.theregister.com/2022/05/24/pypi_ctx_package_compromised/).

## PyTorch torchtriton Dependency Confusion (December 2022)

On December 25, 2022, a researcher registered `torchtriton==2.0.0` on PyPI with a
version number higher than the internal `torchtriton` package hosted on PyTorch’s
private index.
Because pip resolves public PyPI before private indices by default, anyone
who installed PyTorch nightly on Linux between December 25 and December 30, 2022, pulled
the malicious public package instead.

**Affected versions:** `torchtriton==2.0.0` on PyPI (the legitimate package lived on
PyTorch’s private index at `download.pytorch.org`).

**Payload:** a malicious binary at `PYTHON_SITE_PACKAGES/triton/runtime/triton` that
collected hostname, username, working directory, `/etc/hosts`, `/etc/passwd`,
`~/.gitconfig`, `~/.ssh/*`, and the first 1000 files in `$HOME`, exfiltrating via
encrypted DNS queries to `*.h4ck.cfd`.

**Scale:** approximately 2,700 downloads in the five-day window.

**Remediation:** PyTorch removed the `torchtriton` dependency and replaced it with
`pytorch-triton`. A placeholder dummy package was registered on PyPI to prevent reuse.

**Sources:**
[PyTorch official blog](https://pytorch.org/blog/compromised-nightly-dependency/);
[SentinelOne](https://www.sentinelone.com/blog/pytorch-dependency-torchtriton-supply-chain-attack/);
[BleepingComputer](https://www.bleepingcomputer.com/news/security/pytorch-discloses-malicious-dependency-chain-compromise-over-holidays/);
[ReversingLabs](https://www.reversinglabs.com/blog/pytorch-supply-chain-attack-dependency-confusion-burns-devops).

## Ultralytics YOLO Cryptominer (December 2024)

On December 4, 2024, an attacker exploited a GitHub Actions script injection
vulnerability in the Ultralytics YOLO repository (a computer-vision library with ~60M
PyPI downloads and 30K+ GitHub stars).
Two malicious pull requests submitted by the `@openimbot` account triggered a
`pull_request_target` workflow with unsafe template expressions, allowing the attacker
to inject code into the build pipeline.

**Affected versions:** `ultralytics==8.3.41`, `8.3.42`, `8.3.45`, `8.3.46`.

**Payload:** XMRig cryptocurrency miner embedded in the published wheel, executing on
import. The initial compromise (8.3.41) was live for ~12 hours.
Version 8.3.42, intended as a fix, shipped the same malicious code because maintainers
did not fully locate the compromise.
A second wave (8.3.45, 8.3.46) followed on December 7 using a stolen PyPI API token.

**Sources:**
[PyPI official blog](https://blog.pypi.org/posts/2024-12-11-ultralytics-attack-analysis/);
[ReversingLabs](https://www.reversinglabs.com/blog/compromised-ultralytics-pypi-package-delivers-crypto-coinminer);
[Snyk](https://snyk.io/blog/ultralytics-ai-pwn-request-supply-chain-attack/);
[The Hacker News](https://thehackernews.com/2024/12/ultralytics-ai-library-compromised.html);
[Wiz](https://www.wiz.io/blog/ultralytics-ai-library-hacked-via-github-for-cryptomining).

## LiteLLM / TeamPCP (March 2026)

On March 24, 2026, the threat actor TeamPCP published backdoored versions of the
`litellm` Python package after stealing the maintainer’s PyPI credentials.
The credential theft originated from a compromised Trivy GitHub Action used in LiteLLM’s
CI/CD security scanning workflow, which exfiltrated the `PYPI_PUBLISH` token from the
GitHub Actions runner environment.

**Affected versions:** `litellm==1.82.7`, `litellm==1.82.8`. Both were live for
approximately 40 minutes (from 10:39 UTC) before PyPI quarantined them.
Last known clean release: `litellm==1.82.6`.

**Payload:** three-stage attack: credential harvesting (AWS, GCP, Azure, Kubernetes,
GitHub, npm, Slack, Discord tokens), lateral movement across Kubernetes clusters, and a
persistent systemd backdoor polling for additional payloads.
Version 1.82.8 added a `litellm_init.pth` file that triggered at Python interpreter
startup via the `site` module, firing even without an explicit `import litellm`.

**Scale:** ~119,000 downloads in the 40-minute window (LiteLLM has ~95M monthly
downloads).

**Advisory:** GHSA-5mg7-485q-xm76.

**Sources:**
[PyPI incident report](https://blog.pypi.org/posts/2026-04-02-incident-report-litellm-telnyx-supply-chain-attack/);
[Datadog Security Labs](https://securitylabs.datadoghq.com/articles/litellm-compromised-pypi-teampcp-supply-chain-campaign/);
[Snyk](https://snyk.io/blog/poisoned-security-scanner-backdooring-litellm/);
[LiteLLM official advisory](https://docs.litellm.ai/blog/security-update-march-2026);
[GHSA-5mg7-485q-xm76](https://advisories.gitlab.com/pypi/litellm/GHSA-5mg7-485q-xm76/).

## TanStack Worm Cross-Ecosystem Propagation (May 2026)

On May 11, 2026, stolen CI/CD tokens from the TanStack npm worm (Mini Shai-Hulud) were
used to publish malicious versions to PyPI. This is the first documented cross-ecosystem
propagation in the 2025-2026 supply-chain campaign.

**Affected versions:** `mistralai==2.4.6`, `guardrails-ai==0.10.1`. Mistral AI never
released version 2.4.6; the attacker published directly to PyPI.

**Payload:** a Python dropper that downloads `transformers.pyz` from an
attacker-controlled domain and executes it.
The `mistralai` payload includes country-aware logic (avoids Russian-language
environments) and a geofenced destructive branch.
The `guardrails-ai==0.10.1` payload executes on import.

**Advisories:** `GHSA-wx9m-wx4f-4cmg` (`mistralai`); `GHSA-xmpw-2vmm-p4p6` /
CVE-2026-45758 (`guardrails-ai`); the npm side is the umbrella `GHSA-g7cv-rxg3-hmpx` /
CVE-2026-45321.

**Sources:**
[The Hacker News](https://thehackernews.com/2026/05/mini-shai-hulud-worm-compromises.html);
[SafeDep](https://safedep.io/mass-npm-supply-chain-attack-tanstack-mistral/);
[Wiz](https://www.wiz.io/blog/mini-shai-hulud-strikes-again-tanstack-more-npm-packages-compromised);
[BleepingComputer](https://www.bleepingcomputer.com/news/security/shai-hulud-attack-ships-signed-malicious-tanstack-mistral-npm-packages/);
[SecurityWeek](https://www.securityweek.com/tanstack-mistral-ai-uipath-hit-in-fresh-supply-chain-attack/).

## PyTorch Lightning (April 2026)

On April 30, 2026, malicious `pytorch-lightning` versions were published to PyPI using
stolen maintainer credentials, part of the same Mini Shai-Hulud campaign.
They were quarantined roughly 42 minutes after publication.

**Affected versions:** `pytorch-lightning==2.6.2`, `pytorch-lightning==2.6.3`. Last
known clean release: `pytorch-lightning==2.6.1`. This is the PyPI counterpart to the npm
`lightning@2.6.2` / `2.6.3` versions in the same wave.

**Payload:** an obfuscated payload staged in a hidden `_runtime` directory that executes
on import; it harvests credentials, tokens, and cloud secrets and plants persistence
hooks targeting Claude Code and VS Code, among the first malware observed deliberately
targeting AI coding agents.

**Advisory:** `GHSA-w37p-236h-pfx3` / CVE-2026-44484.

**Sources:**
[GHSA-w37p-236h-pfx3](https://github.com/Lightning-AI/pytorch-lightning/security/advisories/GHSA-w37p-236h-pfx3);
[Semgrep](https://semgrep.dev/blog/2026/malicious-dependency-in-pytorch-lightning-used-for-ai-training/);
[Socket](https://socket.dev/blog/lightning-pypi-package-compromised).

## Microsoft durabletask / TeamPCP Wave 4 (May 2026)

On May 19, 2026, three trojanized versions of `durabletask` (the Python SDK for the
Durable Task Framework, ~417K monthly downloads) were published within a 35-minute
window and quarantined by PyPI within hours.
The PyPI token had been harvested from an earlier GitHub breach; the modified builds
were uploaded via twine with no corresponding tags, commits, or CI runs in the source
repo, the now-familiar “publish from a stolen token, not from source” pattern.

**Affected versions:** `durabletask==1.4.1`, `durabletask==1.4.2`, `durabletask==1.4.3`.
Last known clean release: `durabletask==1.4.0`.

**Payload:** a dropper at the top of the source files fetches a 28 KB second-stage
zipapp (`rope.pyz`) from a freshly-registered C2 and executes it silently.
The second stage is a modular credential harvester (AWS, Azure, GCP, Kubernetes,
HashiCorp Vault, 1Password, Bitwarden, `pass`, `gopass`, and 90+ developer-tool configs)
with worm propagation: inside AWS it spreads to other instances via SSM; inside
Kubernetes via `kubectl exec`.

**Sources:** [Wiz](https://www.wiz.io/blog/durabletask-teampcp-supply-chain-attack);
[Snyk](https://snyk.io/blog/durabletask-pypi-supply-chain-attack/);
[Endor Labs](https://www.endorlabs.com/learn/trojanized-microsoft-sdk-durabletask-1-4-1-through-1-4-3-deliver-credential-stealing-malware);
[SafeDep](https://safedep.io/malicious-durabletask-pypi-supply-chain-attack/);
[StepSecurity](https://www.stepsecurity.io/blog/microsofts-durabletask-pypi-package-compromised-in-supply-chain-attack).

* * *

# Part 3: Best Practices For Hardening

## How Pip/uv Config Precedence Works

This is the single most important fact in the document, because the entire hardening
strategy depends on it.

### pip Precedence

```
HIGHEST PRIORITY  ->  command-line flag (--uploaded-prior-to, --only-binary, etc.)
                  ->  environment variable (PIP_* prefix)
                  ->  PIP_CONFIG_FILE (if set; loaded last among config files)
                  ->  site config ($VIRTUAL_ENV/pip.conf inside a virtualenv)
                  ->  user config (~/.config/pip/pip.conf; legacy ~/.pip/pip.conf)
                  ->  global config (/etc/pip.conf, /etc/xdg/pip/pip.conf)
LOWEST PRIORITY   ->  pip builtin defaults
```

Pip does **not** read `[tool.pip]` in `pyproject.toml` or `setup.cfg` as a configuration
source for install hardening.
Project metadata in `pyproject.toml` can declare dependencies, extras, and PEP 517 build
backends, but it does not override or supplement pip’s INI-based config layers.

### uv Precedence

```
HIGHEST PRIORITY  ->  command-line flag (--exclude-newer, --only-binary, etc.)
                  ->  environment variable (UV_* prefix)
                  ->  project-local config (pyproject.toml [tool.uv], uv.toml)
                  ->  user config (~/.config/uv/uv.toml)
LOWEST PRIORITY   ->  uv builtin defaults
```

Implications:

- Settings in user config can be silently overridden by any project-local
  `pyproject.toml`, including ones that arrive via `git clone` of a third-party repo.
- Environment variables cannot be overridden by any config file.
  Only an explicit command-line flag beats them, and explicit flags are visible to the
  user running the command.
- `PIP_<OPTION>` is the documented prefix for pip; dashes in the option name become
  underscores (`--only-binary` becomes `PIP_ONLY_BINARY`).
- `UV_<OPTION>` is the documented prefix for uv (`--exclude-newer` becomes
  `UV_EXCLUDE_NEWER`).

**Operational conclusion:** set hardening as environment variables, not as config-file
entries.
Use config files only as a fallback for processes that do not source shell init.

## The Three-Control Hardening Pattern

Each control attacks a different stage of the kill chain.
Apply all three.

### Control 1: Date-Pinned Install Quarantine

Refuses to install any version published after a rolling cutoff.

- **uv:** `UV_EXCLUDE_NEWER="7 days"`. Accepts friendly durations natively.
  No date arithmetic needed.
  The environment variable works for `uv pip install`, `uv sync`, `uv lock`, and
  `uv add`.
- **pip (>=26.1):** `PIP_UPLOADED_PRIOR_TO="P7D"`. ISO 8601 duration.
  Introduced in pip 26.0 with absolute timestamps; relative-duration support added in
  pip 26.1 (April 2026).
- **pip (<26.1):** no native rolling quarantine.
  Compute an absolute timestamp in shell init:
  `export PIP_UPLOADED_PRIOR_TO="$(date -u -v-7d '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u -d '7 days ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null)"`.
- **pdm:** `pdm lock --exclude-newer <date>` and `pdm install --exclude-newer <date>`.
  Accepts ISO 8601 timestamps and relative durations in `N{d|h|w}` format (e.g. `7d`,
  `3w`). Configurable in `pyproject.toml` under `[tool.pdm.resolution]`.
- **poetry (>=2.4.0):** `solver.min-release-age` in Poetry’s config.
  Filters package versions by upload timestamp during dependency resolution.
  Requires the package source to expose upload timestamps.
  Configure with `poetry config solver.min-release-age 7` (days).
  Available since Poetry 2.4.0 (May 2026).
- **pipx:** inherits from pip or uv depending on backend; set the corresponding env var.
- **conda/mamba:** no native equivalent.

**Catches:** every recent attack.
Malicious versions are detected within minutes-to-hours and yanked, but they remain
“published after my cutoff” for 7+ days regardless.

**Bypass per command:** `UV_EXCLUDE_NEWER= uv pip install some-pkg` or
`PIP_UPLOADED_PRIOR_TO= pip install some-pkg`.

### Control 2: Refuse Source Distribution Builds

Source distributions (`sdist`) execute arbitrary Python code during installation via
`setup.py`, `setup.cfg` hooks, or PEP 517 build backends.
Wheels do not execute code at install time.

- **pip:** `PIP_ONLY_BINARY=":all:"` or `pip install --only-binary :all:`.
- **uv:** `UV_NO_BUILD=true` (equivalent to `--no-build`; refuses to build any source
  distribution). uv prefers wheels by default but will fall back to sdists unless this is
  set. uv does not expose `--only-binary` as an environment variable; the `--only-binary`
  flag is available on the CLI and as `only-binary` under `[tool.uv.pip]` in
  `pyproject.toml` / `uv.toml`.
- **uv (project mode):** set `no-build = true` in `[tool.uv]` in `pyproject.toml` or
  `uv.toml`.
- **uv (pip-mode project config):** set `only-binary = [":all:"]` in `[tool.uv.pip]` if
  you prefer project-level config over the env var.
- **pipx:** inherits from pip or uv; set the corresponding env var.
- **poetry:** no direct equivalent for refusing sdists.
  Poetry builds from sdist when no wheel is available.
  Ensure all dependencies publish wheels where possible.
- **pdm:** no direct equivalent.
- **conda/mamba:** conda packages are always pre-built; no sdist execution risk.

**Caveat:** some legitimate packages do not publish wheels for all platforms (packages
with C extensions on uncommon architectures, for example).
For those, opt out per command: `UV_NO_BUILD= uv pip install some-c-extension-pkg`.

### Control 3: Frozen Lockfile With Hash Pinning

Lockfiles pin exact versions.
Hash pinning verifies the downloaded artifact matches the hash recorded at lock time,
defeating registry tampering and man-in-the-middle attacks.

- **uv:** `uv lock` generates `uv.lock` with hashes by default.
  `uv sync --frozen` refuses to install if the lockfile would change.
- **pip:** `pip install --require-hashes -r requirements.txt`. Generate hashed
  requirements with `pip-compile --generate-hashes` (from `pip-tools`) or
  `uv pip compile --generate-hashes`.
- **poetry:** `poetry.lock` includes hashes by default.
  `poetry install --no-update` installs from the lockfile without re-resolving.
- **pdm:** `pdm.lock` includes hashes by default.
  `pdm install --frozen-lockfile` refuses to install if the lockfile would change.
- **pipx:** uses pip or uv under the hood; no lockfile of its own.
  Pin global tools to specific versions: `pipx install some-tool==1.2.3`.
- **conda/mamba:** `conda-lock` generates cross-platform lockfiles with hashes.
  `conda install --file conda-lock.yml` for reproducible installs.

## Per-Package-Manager Coverage Matrix

| Control | pip >=26.1 | uv | pipx | poetry | pdm | conda/mamba |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| Date-pinned quarantine | `--uploaded-prior-to` (rolling P7D) | `--exclude-newer` (rolling “7 days”) | inherits from backend | `solver.min-release-age` (days, >=2.4.0) | `--exclude-newer` (date or relative) | no |
| Refuse sdist builds | `--only-binary :all:` | `--only-binary :all:` or `no-build = true` | inherits from backend | no native flag | no native flag | N/A (pre-built only) |
| Frozen lockfile with hashes | `--require-hashes` | `uv sync --frozen` (hashes in `uv.lock`) | no lockfile | `poetry install --no-update` (hashes in `poetry.lock`) | `pdm install --frozen-lockfile` (hashes in `pdm.lock`) | `conda-lock` |
| Hash pinning in lockfile | via `pip-compile --generate-hashes` | automatic in `uv.lock` | N/A | automatic in `poetry.lock` | automatic in `pdm.lock` | via `conda-lock` |

**Strategic takeaway:**

- **uv projects** get all three protections natively with the simplest configuration;
  strongest posture.
- **pip >=26.1 projects** get date quarantine and binary-only installs natively.
  Hash pinning requires `pip-tools` or `uv pip compile` to generate hashed requirements.
- **poetry (>=2.4.0) and pdm projects** have strong lockfile-with-hash support and now
  have date quarantine (`solver.min-release-age` for poetry, `--exclude-newer` for pdm)
  but lack binary-only enforcement.
- **conda/mamba** has no sdist execution risk (packages are pre-built) but no date
  quarantine. Defense relies on the conda-forge review process and `conda-lock`.
- **pipenv** (legacy) supports `Pipfile.lock` with hashes but has no date quarantine or
  binary-only flag. Consider migrating to uv or poetry.

**Recommendation for new projects:** prefer uv for its supply-chain hardening surface
area.

## The Single Source-of-Truth Hardening Script

Create one file, `~/.pypi-hardening.sh`, in POSIX shell syntax.
Source it from every shell init that matters.
The same file works on macOS, Linux, and WSL.

```sh
# ~/.pypi-hardening.sh -- POSIX sh; works in bash, zsh, dash, sh

# Rolling 7-day quarantine for uv. Friendly duration; no date arithmetic.
export UV_EXCLUDE_NEWER="7 days"

# Rolling 7-day quarantine for pip >=26.1. ISO 8601 duration.
export PIP_UPLOADED_PRIOR_TO="P7D"

# Refuse source distributions. Blocks setup.py code execution at install time.
# UV_NO_BUILD is the uv equivalent of --no-build. uv does not expose an env var
# named UV_ONLY_BINARY; use this or set only-binary in [tool.uv.pip] project config.
export PIP_ONLY_BINARY=":all:"
export UV_NO_BUILD=true
```

The next several sections wire this file into each platform and shell.

## Setup: macOS

### zsh (macOS Default Since 10.15)

zsh on macOS reads `~/.zshenv` for every invocation: interactive, login, scripts,
subshells. Adding the sourcer there gives universal coverage.

```sh
# Append to ~/.zshenv
[ -r "$HOME/.pypi-hardening.sh" ] && . "$HOME/.pypi-hardening.sh"
```

### bash (Interactive)

```sh
# Append to ~/.bashrc
[ -r "$HOME/.pypi-hardening.sh" ] && . "$HOME/.pypi-hardening.sh"
```

### bash (Login)

macOS Terminal.app opens login shells by default.
iTerm2, VSCode, and most agent terminals open non-login shells.
Cover both by adding the sourcer to both `~/.bash_profile` (or `~/.profile`) and
`~/.bashrc`.

```sh
# Append to ~/.bash_profile or ~/.profile (whichever exists; create if neither)
[ -r "$HOME/.pypi-hardening.sh" ] && . "$HOME/.pypi-hardening.sh"
```

### fish

```fish
# Append to ~/.config/fish/conf.d/pypi-hardening.fish
set -gx UV_EXCLUDE_NEWER "7 days"
set -gx PIP_UPLOADED_PRIOR_TO "P7D"
set -gx PIP_ONLY_BINARY ":all:"
set -gx UV_NO_BUILD true
```

fish does not source POSIX files cleanly, so reproduce the exports directly.
Files under `~/.config/fish/conf.d/` are auto-sourced.

### Verification (Any Shell On macOS)

```sh
echo "$UV_EXCLUDE_NEWER"       # 7 days
echo "$PIP_UPLOADED_PRIOR_TO"  # P7D
echo "$PIP_ONLY_BINARY"        # :all:
echo "$UV_NO_BUILD"            # true
```

## Setup: Linux (Debian/Ubuntu/Fedora/RHEL/Arch)

### bash (Interactive, Non-Login)

`~/.bashrc` is the workhorse on most distros and gets sourced by every interactive bash.

```sh
# Append to ~/.bashrc
[ -r "$HOME/.pypi-hardening.sh" ] && . "$HOME/.pypi-hardening.sh"
```

### bash (Login)

Useful for SSH sessions and terminal multiplexers that launch login shells.

```sh
# Append to ~/.bash_profile or ~/.profile (whichever exists)
[ -r "$HOME/.pypi-hardening.sh" ] && . "$HOME/.pypi-hardening.sh"
```

### zsh

```sh
# Append to ~/.zshenv
[ -r "$HOME/.pypi-hardening.sh" ] && . "$HOME/.pypi-hardening.sh"
```

### fish

Same recipe as macOS fish above.

### systemd User Environment (Linux-Specific)

The cleanest way to make the variables present in every process started by a user
session, including non-interactive children launched by GUI applications or systemd user
units, is `environment.d`:

```ini
# ~/.config/environment.d/pypi-hardening.conf
UV_EXCLUDE_NEWER=7 days
PIP_UPLOADED_PRIOR_TO=P7D
PIP_ONLY_BINARY=:all:
UV_NO_BUILD=true
```

## Setup: Windows

### PowerShell 7 (pwsh)

Find your profile path with `$PROFILE` in PowerShell.
Common location: `C:\Users\<you>\Documents\PowerShell\Microsoft.PowerShell_profile.ps1`.
Create the file if it does not exist.

```powershell
# Append to $PROFILE
$env:UV_EXCLUDE_NEWER = "7 days"
$env:PIP_UPLOADED_PRIOR_TO = "P7D"
$env:PIP_ONLY_BINARY = ":all:"
$env:UV_NO_BUILD = "true"
```

### PowerShell 5 (Windows PowerShell)

Profile path:
`C:\Users\<you>\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`. Same body
as PS7.

### Persistent User-Wide (Survives Reboot, Visible To All Shells)

Setting the variables in the user’s registry hive makes them visible to cmd, PowerShell,
and any GUI-launched process the user starts:

```powershell
[Environment]::SetEnvironmentVariable("UV_EXCLUDE_NEWER", "7 days", "User")
[Environment]::SetEnvironmentVariable("PIP_UPLOADED_PRIOR_TO", "P7D", "User")
[Environment]::SetEnvironmentVariable("PIP_ONLY_BINARY", ":all:", "User")
[Environment]::SetEnvironmentVariable("UV_NO_BUILD", "true", "User")
```

### cmd.exe

cmd is rarely used as a primary shell.
If you need it, the persistent registry-based approach above is the only path; cmd has
no init file equivalent to `.bashrc`. The `setx` command writes the same registry
entries:

```cmd
setx UV_EXCLUDE_NEWER "7 days"
setx PIP_UPLOADED_PRIOR_TO "P7D"
setx PIP_ONLY_BINARY ":all:"
setx UV_NO_BUILD "true"
```

Note: `setx` does not affect the current cmd session; open a new shell to pick up the
values.

### Git Bash

Git Bash reads POSIX init files at `~/.bashrc` and `~/.bash_profile`. Drop the same
`~/.pypi-hardening.sh` into your Git Bash home directory (path resolves to something
like `C:\Users\<you>\.pypi-hardening.sh`), then add the sourcer line to `~/.bashrc`:

```sh
[ -r "$HOME/.pypi-hardening.sh" ] && . "$HOME/.pypi-hardening.sh"
```

### WSL (Ubuntu, Debian, Fedora Under Windows)

WSL behaves like Linux.
Follow the Linux recipes above.
The Windows-side environment variables do not automatically propagate into WSL by
default; configure WSL’s user environment independently.

## Setup: CI Runners

CI environments do not source user shell init.
Inject the variables into the runner’s environment explicitly.

### GitHub Actions

```yaml
env:
  UV_EXCLUDE_NEWER: "7 days"
  UV_NO_BUILD: "true"
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

### GitLab CI

```yaml
variables:
  UV_EXCLUDE_NEWER: "7 days"
  UV_NO_BUILD: "true"
  PIP_ONLY_BINARY: ":all:"
  PIP_UPLOADED_PRIOR_TO: "P7D"
```

### CircleCI, Buildkite, Jenkins

Same pattern: set the four variables in the job environment.

## Install-Script Controls And Source Distribution Safety

Unlike npm, Python’s primary install-time code execution risk comes from source
distributions (sdists), not lifecycle hooks.
When pip builds an sdist, it executes `setup.py` (or a PEP 517 build backend) with full
access to the filesystem and network.
Wheels bypass this entirely.

### Why Refusing sdists Is The Primary Defense

Setting `PIP_ONLY_BINARY=":all:"` for pip and `UV_NO_BUILD=true` for uv forces the
installer to refuse any package that does not have a pre-built wheel available.
This eliminates the entire class of `setup.py`-based attacks.

Note: pip’s `--only-binary` flag has the env-var equivalent `PIP_ONLY_BINARY` (pip
auto-derives `PIP_<OPTION>` for every command-line flag).
uv exposes `UV_NO_BUILD` (equivalent to `--no-build`) but does not expose an env var
named `UV_ONLY_BINARY`. To get `--only-binary` semantics at project scope in uv, set
`only-binary = [":all:"]` under `[tool.uv.pip]` in `pyproject.toml` or `uv.toml`.

### When You Need An sdist

Some packages (especially those with C extensions on uncommon platforms) only distribute
sdists. For those specific packages, opt out narrowly:

```sh
# uv: allow sdist for one command
UV_NO_BUILD= uv pip install some-c-extension-pkg

# pip: allow sdist for one package
pip install --only-binary :all: --no-binary some-c-extension-pkg some-c-extension-pkg
```

### Build Isolation

Both pip and uv support build isolation (`--no-build-isolation` to disable it).
Build isolation runs the sdist build in a temporary virtual environment, limiting (but
not eliminating) the blast radius of malicious build scripts.
Leave isolation enabled (the default) when you must build from sdist.

## IOC Feeds

Use multiple feeds. Each has gaps; the union catches everything in practice.

### Tier 1: Free, Machine-Readable, Comprehensive

| Feed | Coverage | How To Consume | Update Lag |
| --- | --- | --- | --- |
| **OSV.dev** | All ecosystems including PyPI; malicious packages tagged with `MAL-*` IDs | REST: `POST https://api.osv.dev/v1/query`; bulk via `osv-scanner`; raw Git mirror at `github.com/google/osv.dev` | Minutes after upstream advisory |
| **GitHub Advisory Database (GHSA)** | Backs `pip-audit`; PyPI plus several other ecosystems | `gh api graphql` for `securityAdvisories`; `pip-audit` for installed packages | Minutes |
| **PyPA Advisory Database** | Python-specific advisories curated by the Python Packaging Authority | `github.com/pypa/advisory-database`; consumed by `pip-audit` and `safety` | Hours to days |
| **deps.dev** (Google) | Dependency graph and vulnerability rollups | REST: `GET https://api.deps.dev/v3/systems/pypi/packages/<name>` | Same as OSV (shares data) |

### Tier 2: Free Public Feeds With Attack-Specific Reporting

| Feed | Coverage | How To Consume |
| --- | --- | --- |
| **PyPI Blog** | Official incident reports with technical detail (LiteLLM, Ultralytics) | `blog.pypi.org` |
| **Aikido Intel** | Live tracker; novel-attack writeups; affected-package lists for every named campaign | Web at `aikido.dev/intel` |
| **StepSecurity Blog** | Frequently the first public detector; publishes IOC tables | RSS at `stepsecurity.io/blog/feed` |
| **Socket.dev Advisories** | Per-package risk scoring; novel-attack tracking | `socket.dev/pypi/package/<name>` |
| **Datadog Security Labs** | Deep technical posts on campaign attribution and payload analysis | `securitylabs.datadoghq.com` |
| **CISA Alerts** | US-CERT advisories for major incidents | `cisa.gov/news-events/alerts` |

### Tier 3: Commercial (For SLAs Or Private-Package Coverage)

- **Snyk Vulnerability DB**: comprehensive; paid above small-team tier.
- **Phylum**: built around supply-chain-attack use case specifically.
- **ReversingLabs Spectra Assure**: deep binary analysis of published packages.
- **Sonatype OSS Index**: free public read-only API; paid for advanced features.

## Local Scanning Tools

The chain: snapshot what is installed, check against feeds, act.

### `osv-scanner` (Google, Free, Go Binary)

Recommended baseline.
Install prebuilt binaries from `github.com/google/osv-scanner/releases` for
macOS/Linux/Windows, or
`go install github.com/google/osv-scanner/v2/cmd/osv-scanner@latest`.

```bash
# scan lockfiles (osv-scanner V2 syntax; "scan source" is the default subcommand)
osv-scanner scan source -L requirements.txt
osv-scanner scan source -L uv.lock
osv-scanner scan source -L poetry.lock

# scan recursively from cwd
osv-scanner scan source -r .

# offline mode (download DB once, scan in air-gapped env)
osv-scanner scan source --offline --download-offline-databases ./osvdb
```

Supports `requirements.txt`, `uv.lock`, `poetry.lock`, `pdm.lock`, `Pipfile.lock`, plus
16+ other ecosystems.
V2 added transitive scanning for `requirements.txt` via the deps.dev API. Output JSON
with `--format json`.

### `pip-audit` (PyPA / Trail of Bits, Free)

```bash
# install
pip install pip-audit
# or
uv tool install pip-audit

# audit the current environment
pip-audit

# audit a requirements file
pip-audit -r requirements.txt

# use OSV as the vulnerability source (recommended for supply-chain focus)
pip-audit --vulnerability-service osv
```

Backed by PyPA Advisory Database and optionally OSV. Run after every dependency change.

### `safety` CLI (Safety / PyUp, Free Tier)

```bash
# install
pip install safety

# scan the current directory (Safety 3.x recommended command; finds manifests recursively)
safety scan

# legacy command (still supported in Safety 3.x, identical to Safety 2.x behavior)
safety check -r requirements.txt
```

`safety scan` (Safety 3.x) recursively discovers all Python dependency manifests and
virtual environments in the target directory.
`safety check` remains supported for backward compatibility.
Free tier covers public packages.
Paid tier adds monitoring and CI integration.

### Manual Lockfile Grep Against A Known-Bad List

When a brand-new IOC list drops and you do not want to wait for `osv-scanner` to ingest
it, grep directly:

```bash
#!/usr/bin/env bash
# Usage: scan-pypi-iocs.sh /path/to/requirements-or-lockfile  ioc1==ver  ioc2==ver ...
FILE="$1"; shift
for ioc in "$@"; do
  pkg="${ioc%%==*}"; ver="${ioc##*==}"
  grep -qiE "${pkg}[= ]+${ver}" "$FILE" && echo "HIT: $ioc"
done
```

## Operational Checklist

### Initial Setup (Every Workstation)

- [ ] Create `~/.pypi-hardening.sh` (or platform equivalent).
- [ ] Hook it from every shell init that matters: bash plus zsh, login plus non-login.
- [ ] Verify: `echo "$UV_EXCLUDE_NEWER"`, `echo "$PIP_ONLY_BINARY"`.
- [ ] Run `pip-audit` in each active virtual environment; investigate any hits.
- [ ] Rotate any plaintext PyPI tokens to scoped, read-only tokens where possible.

### Per-Project (When Adding Or Removing Dependencies)

- [ ] To intentionally install a fresh package, explicitly unset the quarantine
  variables per command, visibly: `UV_EXCLUDE_NEWER= UV_NO_BUILD= uv add some-pkg`.
- [ ] After lockfile change, run `osv-scanner scan source -L <lockfile>` or `pip-audit`.
- [ ] Commit lockfile.

### Weekly

- [ ] Skim PyPI Blog, Aikido Intel, StepSecurity, and Datadog Security Labs for new
  named attacks. Add their IOC lists to a local `known-bad.txt` if relevant.
- [ ] Run `pip-audit` in active environments.

### When A New Named Attack Drops

- [ ] Run the grep recipe against every lockfile and `requirements.txt` in your
  workspace with that attack’s IOC list.
- [ ] If you have hits: revoke every PyPI, GitHub, and cloud token reachable from any
  machine that ran `pip install` while the malicious version was live.
  Check `~/.pypirc`, `~/.aws/credentials`, `~/.config/gcloud/`, `~/.config/gh/` for
  traces.
- [ ] Pin to the last known-good version.
  Regenerate the lockfile with `uv lock` or `pip-compile --generate-hashes`. Commit.
- [ ] Subscribe to the affected project’s GitHub Security Advisories.

## Common Questions

**Does the date quarantine block legitimate security patches that landed in the last 7
days?** Yes, by design.
The trade-off: 7 days of delayed security patches versus zero days of supply-chain
malware exposure. Historically the latter has been the bigger source of incidents for
typical projects. For genuinely urgent CVEs (a 0-day RCE), opt out per command.

**How does this interact with Renovate or Dependabot?** Renovate supports
`minimumReleaseAge: "7 days"` in `renovate.json`, which applies to all ecosystems
including PyPI. Dependabot does not yet support release-age gating for PyPI (as of
2026-05). Both tools’ filters are independent of the package manager’s; both should be
on.

**What about `--only-binary :all:` breaking packages that only publish sdists?** Most
widely-used packages publish wheels.
The long tail of sdist-only packages is shrinking as PyPI Trusted Publishers and
automated wheel-building services (cibuildwheel) become standard.
For the remaining cases, opt out per package as shown in the install-script controls
section above.

**Is conda/mamba safe from these attacks?** conda packages are pre-built, so there is no
`setup.py` execution risk.
The main risk surface is the conda-forge review process: a compromised feedstock could
publish a malicious conda package, but this has not been observed at scale.
The May 2026 cross-ecosystem propagation did not reach conda.
Use `conda-lock` for hash-pinned reproducible environments.

**My CI runs `uv sync --frozen`. Am I safe?** Only as safe as your lockfile.
If a developer ran `uv add` on a fresh machine without the hardening, a malicious
version is now baked into the committed lockfile, and CI installs it.
Defense in depth: enforce hardening in CI too (set variables in the runner before
`uv sync`), and run `pip-audit` or `osv-scanner` in a separate CI job that blocks merge
on findings.

**Does `pipx` inherit these protections?** pipx uses pip or uv as its installation
backend. If the corresponding `PIP_*` or `UV_*` environment variables are set, pipx
inherits them. Verify with `pipx install --verbose some-tool` and check the pip/uv
invocation in the output.

## Updating This Document

This is a living document.
The threat landscape changes on a weeks-to-months cadence; the protections (env-var
pattern, IOC feeds, scanner tools) change on a months-to-years cadence.
Maintain Part 2 (notable exploits) more aggressively than Parts 1 or 3.

Procedures, citation rules, and suggested agent prompts are in
[`self-update-instructions.md`](../self-update-instructions.md) -> “Updating Research
Docs”.

* * *

## Sources

### Attack-Specific Writeups (2022-2026)

- [The Hacker News: Popular PyPI Package ‘ctx’ and PHP Library ‘phpass’ Hijacked to Steal AWS Keys (May 2022)](https://thehackernews.com/2022/05/pypi-package-ctx-and-php-library-phpass.html)
- [Sonatype: PyPI Package ‘ctx’ Compromised (May 2022)](https://www.sonatype.com/blog/pypi-package-ctx-compromised-are-you-at-risk)
- [BleepingComputer: Popular Python and PHP Libraries Hijacked to Steal AWS Keys (May 2022)](https://www.bleepingcomputer.com/news/security/popular-python-and-php-libraries-hijacked-to-steal-aws-keys/)
- [PyTorch: Compromised Nightly Dependency Chain (Dec 2022)](https://pytorch.org/blog/compromised-nightly-dependency/)
- [SentinelOne: PyTorch Dependency ‘torchtriton’ on PyPI Supply Chain Attack (Jan 2023)](https://www.sentinelone.com/blog/pytorch-dependency-torchtriton-supply-chain-attack/)
- [ReversingLabs: PyTorch Supply Chain Attack, Dependency Confusion Burns DevOps (Jan 2023)](https://www.reversinglabs.com/blog/pytorch-supply-chain-attack-dependency-confusion-burns-devops)
- [PyPI Blog: Supply-Chain Attack Analysis, Ultralytics (Dec 2024)](https://blog.pypi.org/posts/2024-12-11-ultralytics-attack-analysis/)
- [ReversingLabs: Compromised Ultralytics PyPI Package Delivers Crypto Coinminer (Dec 2024)](https://www.reversinglabs.com/blog/compromised-ultralytics-pypi-package-delivers-crypto-coinminer)
- [Snyk: Ultralytics AI Pwn Request Supply Chain Attack (Dec 2024)](https://snyk.io/blog/ultralytics-ai-pwn-request-supply-chain-attack/)
- [Wiz: Ultralytics AI Library Hacked via GitHub for Cryptomining (Dec 2024)](https://www.wiz.io/blog/ultralytics-ai-library-hacked-via-github-for-cryptomining)
- [PyPI Blog: Incident Report, LiteLLM/Telnyx Supply-Chain Attacks (Apr 2026)](https://blog.pypi.org/posts/2026-04-02-incident-report-litellm-telnyx-supply-chain-attack/)
- [Datadog Security Labs: LiteLLM and Telnyx Compromised on PyPI, Tracing the TeamPCP Campaign (Mar 2026)](https://securitylabs.datadoghq.com/articles/litellm-compromised-pypi-teampcp-supply-chain-campaign/)
- [Snyk: How a Poisoned Security Scanner Became the Key to Backdooring LiteLLM (Mar 2026)](https://snyk.io/blog/poisoned-security-scanner-backdooring-litellm/)
- [LiteLLM: Security Update, Suspected Supply Chain Incident (Mar 2026)](https://docs.litellm.ai/blog/security-update-march-2026)
- [The Hacker News: Mini Shai-Hulud Worm Compromises TanStack, Mistral AI, Guardrails AI (May 2026)](https://thehackernews.com/2026/05/mini-shai-hulud-worm-compromises.html)
- [SafeDep: Mass Supply Chain Attack Hits TanStack, Mistral AI npm and PyPI Packages (May 2026)](https://safedep.io/mass-npm-supply-chain-attack-tanstack-mistral/)
- [Wiz: Mini Shai-Hulud Strikes Again, TanStack + more npm Packages Compromised (May 2026)](https://www.wiz.io/blog/mini-shai-hulud-strikes-again-tanstack-more-npm-packages-compromised)
- [SecurityWeek: TanStack, Mistral AI, UiPath Hit in Fresh Supply Chain Attack (May 2026)](https://www.securityweek.com/tanstack-mistral-ai-uipath-hit-in-fresh-supply-chain-attack/)
- [BleepingComputer: Shai Hulud Attack Ships Signed Malicious TanStack, Mistral npm Packages (May 2026)](https://www.bleepingcomputer.com/news/security/shai-hulud-attack-ships-signed-malicious-tanstack-mistral-npm-packages/)

### Tools And Feeds

- [OSV.dev, Open Source Vulnerabilities database](https://osv.dev/)
- [OSV-Scanner on GitHub](https://github.com/google/osv-scanner)
- [pip-audit on GitHub (PyPA / Trail of Bits)](https://github.com/pypa/pip-audit)
- [Safety CLI](https://www.getsafety.com/cli)
- [uv documentation (exclude-newer, only-binary)](https://docs.astral.sh/uv/)
- [pip documentation (uploaded-prior-to, only-binary)](https://pip.pypa.io/en/stable/)
- [PyPA Advisory Database](https://github.com/pypa/advisory-database)
- [PyPI Attestations (Sigstore)](https://blog.pypi.org/posts/2024-11-14-pypi-now-supports-digital-attestations/)
- [Socket, supply-chain risk platform](https://socket.dev/)
- [Aikido Intel feed](https://intel.aikido.dev)
- [Snyk Vulnerability Database](https://snyk.io/vuln/)
- [GitHub Advisory Database (PyPI)](https://github.com/advisories?query=type%3Areviewed+ecosystem%3Apip)
- [deps.dev API](https://deps.dev/)

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
