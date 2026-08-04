# Scripts

Audit and reporting tools for the guides in this repo.
Each script is single-file Python, zero third-party dependencies, runnable with `uv run`
(preferred, gives a hermetic Python) or plain `python3`.

The scripts are written in Python rather than Node.js by design: the audit tool should
not ride on the same supply chain it audits.
Python stdlib has decades of stability and is independent of the npm/PyPI/cargo/Go
ecosystems being checked.
Each script declares `dependencies = []` via PEP 723 inline metadata, which `uv`
enforces.

## Scripts

### `audit_npm.py`

Audits installed npm packages against the
[OSV vulnerability database](https://osv.dev/). Primary use case: after
`npm install -g <pkg>`, verify nothing in the transitive dependency tree matches a known
malicious-version advisory.

Usage:

```sh
# Scan the global node_modules (default; resolves $(npm root -g))
uv run scripts/audit_npm.py

# Scan a project's node_modules
uv run scripts/audit_npm.py --node-modules ./node_modules

# Check specific package@version pairs without a directory scan
uv run scripts/audit_npm.py --packages chalk@5.6.1 debug@4.4.2

# Machine-readable output for CI or piping
uv run scripts/audit_npm.py --json > audit.json

# Fallback when uv is not installed (any Python 3.11+):
python3 scripts/audit_npm.py
```

Exit codes:

- `0`: no OSV-known advisories found.
- `1`: one or more ordinary CVE advisories found (no `MAL-*` IDs).
- `2`: error (network failure after retries, invalid arguments, missing target).
- `3`: one or more malicious-package advisories found (at least one `MAL-*` ID).

The script retries OSV requests with bounded exponential backoff (up to 4 attempts,
initial delay 1s, doubling) on HTTP 408 / 429 / 5xx and on transient network errors, so
brief OSV-side outages do not surface as exit 2.

Output format (text mode):

```
Scanned <N> unique package@version pair(s) from <target>.

[MALICIOUS] <pkg>@<ver>            ← tagged only for OSV MAL-* IDs
    - <id>: <summary>
      severity: <CVSS or unspecified>
      ref: <first reference URL>
```

The `[MALICIOUS]` tag is reserved for advisories with IDs starting `MAL-` (OSV’s
dedicated malicious-package corpus).
Ordinary CVEs are listed as `[advisory]`. Both categories return a non-zero exit code.

### `audit_workspace.py`

Audits a repository and the local host for **open-time** and **load-time** persistence:
payloads that execute when a workspace is opened, or on every Python interpreter start,
rather than at package-install time.
A lockfile scan cannot find any of these, because none of them arrive as a package
version. Companion guide:
[`../guidelines/hardening-agent-workspaces.md`](../guidelines/hardening-agent-workspaces.md).

Four independent checks:

- **`autostart`:** editor and agent config that runs a command on open.
  `.vscode/tasks.json` (`runOn: folderOpen`), `.claude/settings.json` hooks,
  `.devcontainer` lifecycle commands, `.mcp.json` servers, `.envrc`, plus known loader
  filenames (`setup.mjs`, `Math_Symbol.js`, `trap-core.js`).
- **`unicode`:** invisible and bidirectional code points in agent instruction files
  (`CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.cursor/rules/*.mdc`), the vector the May
  2026 TrapDoor campaign used to hide instructions from human reviewers.
- **`pth`:** Python `.pth` files that execute code at interpreter startup, the June 2026
  Hades vector. `distutils-precedence.pth` and `__editable__.*` are allow-listed and
  reported as informational.
- **`host`:** the 2026-08-04 keyv worm’s `gh-token-monitor` token-revocation watcher.

Usage:

```sh
# Triage a freshly cloned repo BEFORE opening it in an editor or agent
uv run scripts/audit_workspace.py ./REPO

# Include the active interpreter's site-packages in the .pth check
uv run scripts/audit_workspace.py --scan-site-packages .

# One check only (repeatable), e.g. as a CI gate
uv run scripts/audit_workspace.py --only unicode .

# Machine-readable output
uv run scripts/audit_workspace.py --json .

# Fallback when uv is not installed (any Python 3.11+):
python3 scripts/audit_workspace.py ./REPO
```

Exit codes:

- `0`: no findings.
- `1`: informational findings only (review; commonly benign).
- `2`: error (bad arguments, unreadable target).
- `3`: one or more `HIGH` findings.

`HIGH` means “this executes, or steers an agent, without you asking”; it is a prompt to
read the file, not proof of compromise.
A repository you wrote yourself will legitimately report `HIGH` for its own hooks.
The signal is a `HIGH` finding in a repo you did **not** write, or one that appears in a
repo that previously had none.

The script is read-only.
It never edits, deletes, or executes anything it finds, which matters because the
correct response to a `host` finding is to remove the watcher **before** rotating any
credential: the keyv worm’s watcher runs an operator-supplied handler when a stolen
token stops working.

## Why These Scripts Exist (vs `osv-scanner`)

`osv-scanner` (Google, Go binary) is the canonical tool for scanning lockfiles.
It is the right answer for project-level `package-lock.json` / `pnpm-lock.yaml` /
`yarn.lock` audits. Use it directly:

```sh
osv-scanner scan -L pnpm-lock.yaml
```

`osv-scanner` does not directly scan an already-installed global `node_modules` tree —
there is no lockfile in `$(npm root -g)`. After `npm install -g <pkg>`, the only way to
verify the install via `osv-scanner` is to construct a synthetic lockfile.
`audit_npm.py` fills that gap with a small, single-file Python program that walks the
tree and queries the OSV API directly.

`audit_workspace.py` covers a different gap: it looks for things that are not packages
at all. A committed `SessionStart` hook, a zero-width instruction in `CLAUDE.md`, and a
`.pth` file inside an installed wheel have no `pkg@version` to look up, so no
vulnerability database can report them.
The checks are structural rather than signature-based, which is why the output needs a
human read rather than a pass/fail reflex.

## Auditing the Scripts Themselves

Each script is a single file, top-to-bottom readable, no transitive imports beyond
Python stdlib (`urllib.request`, `json`, `pathlib`, `subprocess` for `npm root -g`).
Read the source before running.

The PEP 723 inline metadata header (`dependencies = []`) makes the “zero deps” claim
machine-verifiable. `uv` enforces it at run time.

## Output Reliability

Two known sources of OSV-API friction the script handles explicitly:

1. **Overly-broad SEMVER ranges in advisories.** Some OSV advisories declare
   `affected.ranges = [{events: [{introduced: 0}]}]` with no `fixed` event, which OSV’s
   matching logic treats as “all versions affected”.
   When the same advisory also provides an explicit `affected.versions` list, that list
   is the canonical narrow set.
   The script filters out matches where the queried version is not in the explicit list.
   See `advisory_affects_version()` in the source.

2. **Word “malicious” in non-malicious CVE summaries.** Many CVE summaries describe
   malicious actors as part of the threat model ("denial of service via a malicious FTP
   server"). The `[MALICIOUS]` tag is reserved for the `MAL-` ID prefix only; a
   summary-text heuristic produces false positives.
   See `is_malicious()` in the source.

## References

- [OSV.dev API documentation](https://google.github.io/osv.dev/api/)
- [OSV-Scanner](https://github.com/google/osv-scanner)
- [OSV vulnerability list for npm](https://osv.dev/list?ecosystem=npm)
- [PEP 723—Inline script metadata](https://peps.python.org/pep-0723/)
- [uv documentation](https://docs.astral.sh/uv/)

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
