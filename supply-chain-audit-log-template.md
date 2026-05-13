# Supply Chain Audit Log

**Owner:** <your name and contact>

**Last updated:** <YYYY-MM-DD>

Chronological record of supply-chain audits performed against this machine or
repository. Entries are appended in reverse-chronological order (newest at top).
Format and procedure are defined in
[guidelines/hardening-npm.md → “Keeping A Supply Chain Audit Log”](https://github.com/jlevy/supply-chain-hardening-guidebook/blob/main/guidelines/hardening-npm.md#keeping-a-supply-chain-audit-log).

Every audit run leaves an entry here.
The goal: a future reader (human or agent) can reconstruct exactly what was checked,
what was found, how each finding was analysed, and what action was taken.

## Redaction Rules

Audit logs are useful precisely because they contain raw output.
That makes them a secret-leak hazard.
Before committing or sharing:

- **Never paste live tokens, secrets, private keys, or cookie strings.** Replace with
  `[REDACTED token id <last-4>]` or similar.
  This includes anything from `~/.npmrc` `_authToken=`, `~/.pypirc` passwords,
  `~/.cargo/credentials.toml`, `~/.config/gh/hosts.yml`, environment dumps, and shell
  history snippets.
- **Redact internal hostnames, internal package names, and customer identifiers** when
  the log will be shared outside a small team.
  The redaction marker should still convey shape (e.g. `internal-cluster-[REDACTED]`
  rather than removing the line entirely).
- If the log is gitignored and lives only on a personal machine, redaction can be
  lighter — but the file is still on disk and may be exfiltrated by the next malicious
  package. Treat all logs as recoverable.

## Entry Format

Each entry uses the headings below, in order.
Keep empty sections (write “(none)”) rather than omitting them so the format is
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

* * *

## <YYYY-MM-DD> — <Short Title For This Audit>

### Context

| Item | Value |
| --- | --- |
| Date | <YYYY-MM-DD> |
| Auditor | <name; note if assisted by an LLM> |
| OS | <e.g. Darwin 25.x, Ubuntu 24.04, Windows 11> |
| Node | <version; how installed (fnm, nvm, system)> |
| Global node_modules path | <output of `npm root -g`> |
| Package managers | <npm X.Y, pnpm X.Y, yarn X.Y, bun X.Y> |
| Hardening env vars active | <yes/no; list which> |
| Hardening source file | <e.g. ~/.npm-hardening.sh sourced from ~/.zshenv, ~/.bashrc> |

### Scope

- <e.g. `--global` scan of `$(npm root -g)`>
- <e.g. `--node-modules <path>` of a specific project>
- <e.g. positive control: `--packages <known-bad@version> <known-good@version>`>

### Commands Run

```sh
# Replace with exact commands invoked. Examples:
uv run scripts/audit_npm.py --help
uv run scripts/audit_npm.py --packages chalk@5.6.1 debug@4.4.2 chalk@5.6.2
uv run scripts/audit_npm.py
uv run scripts/audit_npm.py --node-modules /path/to/project/node_modules
```

### Raw Findings

Summarise numerically, then list specifics.
Example:

> Scanned <N> unique `(name, version)` pairs.
> Got <K> advisories total; <M> tagged `[MALICIOUS]` via `MAL-*` IDs.

| Package | OSV ID | Type | Notes |
| --- | --- | --- | --- |
| `<pkg>@<ver>` | `<MAL-YYYY-NNNN or GHSA-...>` | Malicious / CVE | <one-line summary> |

### Analysis And Verdict

For each finding that needs more than a one-line entry, write a subsection.
Cover:

- Where the package was installed (file path, transitive-dep chain).
- Install mtime vs the advisory publish date.
- Affected version range per OSV (`versions` list vs SEMVER range).
- Whether the on-disk package has install scripts (`preinstall`, `install`,
  `postinstall`).
- Final call: malicious / false positive / legitimate-CVE-to-track-separately.

Example:

#### `<pkg>@<ver>`

Found at `<path>`. Transitive dep of `<parent-pkg>@<parent-ver>`. Install mtime
`<YYYY-MM-DD HH:MM:SS>` (<N> days before / after the advisory publish date).

OSV `MAL-YYYY-NNNN` details:

- Published: `<ISO timestamp>`.
- Affected `versions`: <list>.
- Affected SEMVER range: <events>.

**Verdict:** <malicious / false positive / regular CVE>. <one-line rationale>.

### Actions Taken

| Time | Action |
| --- | --- |
| &lt;HH:MM&gt; | <e.g. Revoked npm token <id> via `npm token revoke`.> |
| &lt;HH:MM&gt; | <e.g. Downgraded `<pkg>` to `<safe-version>` in `package.json`; ran `pnpm install --before=2026-05-04`. Committed.> |
| &lt;HH:MM&gt; | <e.g. Rotated AWS credentials via IAM console.> |

If no actions taken: `(none)`.

### Pending Actions

- [ ] <Item; owner>
- [ ] <Item; owner>

If nothing pending: `(none)`.

### Verdict (Summary)

<One paragraph: was the machine compromised?
What was the highest-severity real finding?
What still needs to happen?>

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
