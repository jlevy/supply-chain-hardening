# Self-Update Instructions

**Last updated:** 2026-08-06

**Author:** Joshua Levy (github.com/jlevy) with agent assistance

Procedures for keeping the docs in this repo current.
Three doc categories require updates on different cadences:

- **Compromised-packages table** (`compromised-packages.md`): canonical cross-ecosystem
  record of named supply-chain incidents.
  Updated whenever a new incident is multi-source verified.
- **Hardening guidelines** (`hardening-<ecosystem>.md`, plus the cross-ecosystem
  `hardening-ci-cd.md` and `hardening-agent-workspaces.md`): brief operational action
  lists. Update when configuration recipes change (new env var, new flag, new tool
  replacing an old one).
  `hardening-ci-cd.md` covers publish-side and GitHub Actions controls that are not
  specific to one registry; update it when a CI/CD control changes (new GitHub Actions
  setting, new trusted/staged-publishing flow, new runner-hardening option).
  `hardening-agent-workspaces.md` covers open-time execution; update it when an agent or
  editor changes its trust model, hook mechanism, or config file paths, which happens on
  a faster cadence than package-manager changes.
- **Research docs** (`research-<ecosystem>-supply-chain-hardening.md`): full
  threat-model and per-ecosystem-implementation references.
  Update when an ecosystem-specific control set or mechanism changes, or when there is
  enough mechanism detail to warrant a deep-dive subsection on a particular incident.

When a new incident lands, **update `compromised-packages.md` first**, then add
ecosystem-specific narrative or mechanism detail to the relevant research doc.
Hardening guides only need updates if a new control or shell pattern is involved.

**Dated stamps are reserved for currency-sensitive pages.** The pages above (incident
table, hardening playbooks, research docs, and this file) carry a `**Last updated:**`
header because their version-specific and incident-specific claims rot, and the date
tells a reader how stale they might be.
Evergreen methodology pages (`README.md`, `strict-mode.md`,
`untrusted-repo-first-run.md`) deliberately carry **no** date stamp; do not add one.
`tests/validate-docs.py` enforces this split.

## Updating `compromised-packages.md`

This list is **curated, not exhaustive**. The goal is to capture notable, high-impact
incidents that defenders should recognise by name.
Routine typosquats with low download counts, single-source rumours, and minor account
hijacks that did not get multi-source coverage can be omitted.
For the comprehensive cross-ecosystem feeds, point users at OSV.dev, GHSA, RustSec, and
PyPA Advisory DB, those are the systems of record, this file is a quick-reference watch
list.

Update when a notable new supply-chain attack on any ecosystem (npm, PyPI, crates.io, Go
modules, or any future ecosystem covered) is publicly reported by at least two
independent sources from the “Incident Reporting Feeds” list in
[README.md → “Authoritative Sources”](README.md#authoritative-sources), or by CISA. Bar
for inclusion: high download count, novel mechanism, named campaign, or persistence
patterns worth recognising on sight.

`compromised-packages.md` has three sections:

- **Active Watch List (Actionable IOCs)**: rows with exact `pkg@version` (or a
  fully-linked GHSA / full-IOC-list URL), dates, and multi-source references.
  Defenders scan against this section.
  It is **size-capped**: roughly the last twelve months, plus incidents whose artifacts
  are still served (e.g. Go module-proxy caching).
- **Historical Incidents (Recognition Only)**: aged-out rows kept for their mechanism,
  with a one-line pattern description and one or two primary references.
  No per-version IOCs; the systems of record cover those.
- **Contextual Incidents (Unverified / Pending Verification)**: campaigns named in
  trusted feeds but missing per-version detail or independent verification.
  Awareness only; no grep-able IOCs.

Add new rows to the **Active Watch List** when they meet the bar.
Move rows out of Contextual into the Active Watch List when verification is completed,
or delete from Contextual if the campaign turns out to be misattributed.

**Aging rows out:** when an Active row is more than about twelve months old and its
artifacts are no longer served (versions yanked, no proxy cache still delivering the
payload), move it to Historical Incidents: keep Date, Name, Ecosystem, a one-line
pattern description, and one or two primary references; drop the per-version IOC list.
Do not delete rows outright—the recognition value is the point of keeping them.

Procedure:

1. Verify with at least two independent sources from
   [README.md → “Authoritative Sources”](README.md#authoritative-sources) → “Incident
   Reporting Feeds”. Acceptable substitutes: a CISA alert, or a primary maintainer
   postmortem.
2. Append a new row (or rows, one per ecosystem if the campaign hit multiple) to the
   Active Watch List. Match the existing column structure exactly: Date, Name, Ecosystem,
   Scale, Affected `pkg@version` (representative), Vector, References.
3. Quote exact `package@version` strings.
   Do not paraphrase as “version 1.x”.
4. Use links in the `References` column.
   Prefer primary sources (maintainer postmortems, GHSA) over aggregator blogs.
5. Bump the “Last updated” date in the header.
6. If the incident is significant enough to merit ecosystem-specific mechanism detail
   (novel attack vector, novel persistence mechanism, novel IOC patterns), add a
   “Mechanism And Indicators” subsection to the relevant research doc.

Cross-ecosystem campaigns: if the same campaign hit packages in multiple ecosystems
(e.g., the May 2026 TanStack worm propagated to PyPI), record one row per affected
ecosystem so that per-ecosystem audits stay straightforward.

## Updating Hardening Guidelines (`hardening-*.md`)

Update when:

1. A package manager ships a new control relevant to the four-control pattern (date pin,
   rolling quarantine, install-script disable, frozen lockfile).
2. A package manager’s existing flag or env-var name changes.
3. A new commonly-used shell or platform needs a recipe.
4. A new local scanning tool becomes a Tier-1 recommendation in the corresponding
   research doc.

Procedure:

1. Read the current hardening doc end to end.
2. Cross-check against the corresponding research doc.
3. Make the change in both docs if it affects both.
4. Bump the “Last updated” date.

Do not add detail that belongs in the research doc.
The hardening doc is intentionally brief; new background or threat-context goes into the
research doc.

**Keep the cool-off default consistent.** The repo-wide default is **14 days**
(`README.md` → “The Default Policy: A 14-Day Cool-Off”). If that number ever changes,
update it everywhere in lockstep, minding that the control and unit differ by tool:

- npm 11.10+: `NPM_CONFIG_MIN_RELEASE_AGE=14` (days).
- pnpm 10.x: `NPM_CONFIG_MINIMUM_RELEASE_AGE=20160` (minutes).
- pnpm 11+: `minimumReleaseAge: 20160` in `pnpm-workspace.yaml` (minutes); pnpm 11 does
  not read `NPM_CONFIG_*` env vars, only `PNPM_CONFIG_*`.
- Yarn 4.10+: `npmMinimalAgeGate: 20160` in `.yarnrc.yml` (minutes).
- Bun 1.3+: `minimumReleaseAge = 1209600` in `bunfig.toml` (seconds).
- uv: `UV_EXCLUDE_NEWER=”14 days”`; pip 26.1+: `PIP_UPLOADED_PRIOR_TO=”P14D”`; poetry:
  `solver.min-release-age 14` (days).
- The `date -v-14d` / `-d '14 days ago'` shell snippets and
  `npm-check-updates --cooldown 14` examples, plus `SUPPLY-CHAIN-SECURITY.md`,
  `guidelines/strict-mode.md`, and the per-ecosystem playbooks.

Grep for `14`, `20160`, `1209600`, and `P14D` before claiming the change is complete.

**Re-check the shipped defaults, not just the syntax.** pnpm, Yarn, Bun, and Dependabot
each enable a cool-off by default, and those default values move.
The comparison table in `README.md` -> “What the Ecosystems Now Ship by Default” states
a default for every tool and is the thing most likely to go stale; verify each row
against vendor documentation rather than a secondary blog, which is how the Yarn and Bun
rows were wrong in circulating write-ups.

## Updating Research Docs (`research-*-supply-chain-hardening.md`)

Update when:

1. A new named supply-chain attack on the ecosystem is publicly reported by at least two
   independent sources from
   [README.md → “Authoritative Sources”](README.md#authoritative-sources) → “Incident
   Reporting Feeds”, or by CISA.
2. A new package-manager release adds a relevant control (the coverage matrix needs
   flipping).
3. A new authoritative IOC feed launches, or an existing one shuts down or changes its
   URL.
4. A new scanning tool sees broad adoption and becomes a Tier-1 recommendation.

Procedure:

1. Read the entire research doc first.
   Don’t patch in isolation; the exploits table and the IOC-feed section reference each
   other.
2. Verify the new event with at least two independent sources from
   [README.md → “Authoritative Sources”](README.md#authoritative-sources) → “Incident
   Reporting Feeds”. Do not add unverified rumours or single-source claims.
3. Add a row to the exploits table in chronological order with the same column
   structure: date, name, scale, affected packages, vector.
4. Cross-reference any new control in the coverage matrix.
5. Update the trend-line note if cadence changes meaningfully.
6. If the threat profile or control set changes enough to invalidate the hardening doc,
   update that too.
7. Bump the “Last updated” date.
8. Refresh URLs annually.
   Click through each IOC-feed URL once a year; replace dead links with archive.org
   snapshots rather than deleting them.

## Maintaining `tests/known-env-vars.txt`

`tests/validate-docs.py` (run automatically in CI via `.github/workflows/doc-lint.yml`)
checks that every package-manager-shaped env-var name in the docs (`NPM_CONFIG_*`,
`PIP_*`, `UV_*`, `CARGO_*`, and the `GO*` names we use) is in
`tests/known-env-vars.txt`. This catches the “`UV_ONLY_BINARY`-class bug”—a
plausibly-named env var that does not actually exist.

When you introduce a new env var in the docs:

1. Add the name to `tests/known-env-vars.txt`. Include a comment with the
   package-manager version that introduced it.
2. If the env var is one that does not work (e.g. you are documenting a common
   misconception), add it to the “Documented-as-not-supported” section of the allow-list
   with a comment explaining the intent.
3. Run `python3 tests/validate-docs.py` locally; it must exit 0.

## Re-Verifying Package-Manager Versions

The hardening playbooks reference specific package-manager versions (e.g.
`NPM_CONFIG_MIN_RELEASE_AGE` requires npm 11.10+; `MINIMUM_RELEASE_AGE` requires pnpm
10.16.0+). When npm, pnpm, pip, uv, Cargo, or Go publishes a major release, re-verify
before bumping the Last Verified Against table.

### Last Verified Against

| Tool | Version | Verified date | Validator | Notes |
| --- | --- | --- | --- | --- |
| npm | 12.0.2 | 2026-08-04 | agent-assisted refresh | **npm 12 (2026-07-08) blocks dependency lifecycle scripts and implicit `node-gyp` builds by default** via the root package’s `allowScripts` policy, managed with `npm install-scripts ls / approve / deny / prune` plus `npm rebuild`; `allow-git` and `allow-remote` default to `none`, so tarball-URL and git installs need `--allow-remote` / `--allow-git`; unknown `.npmrc` keys error only when `strict-npmrc=true` (default `false`), but unknown **CLI flags** always error; requires Node `^22.22.2 \|\| ^24.15.0 \|\| >=26.0.0`; `npm shrinkwrap` removed. `NPM_CONFIG_MIN_RELEASE_AGE` requires 11.10+; staged publishing requires 11.15+; OIDC trusted publishing requires 11.5.1+ |
| pnpm | 10.x and 11.20.0 | 2026-08-04 | agent-assisted refresh | 10.x reads `NPM_CONFIG_MINIMUM_RELEASE_AGE` (minutes); **pnpm 11 (2026-04-28) no longer reads `npm_config_*`, the env prefix is `PNPM_CONFIG_*` and settings live in `pnpm-workspace.yaml` / `~/.config/pnpm/config.yaml`** ([release notes](https://pnpm.io/blog/releases/11.0)); v11 defaults `minimumReleaseAge: 1440` and `strictDepBuilds: true`; `allowBuilds` map replaced `onlyBuiltDependencies`/`neverBuiltDependencies` |
| pip | 26.2.1 | 2026-08-04 | agent-assisted refresh | `PIP_UPLOADED_PRIOR_TO` accepts ISO 8601 duration in 26.1+ |
| uv | 0.12.1 | 2026-08-04 | agent-assisted refresh | `exclude-newer-package` / `UV_EXCLUDE_NEWER_PACKAGE` gives per-package cool-off overrides (`<pkg>=false` exempts one package); 0.12 rejects MD5-only hashes in hash-checking mode, rejects wheels that could replace the Python interpreter, rejects name-mismatched distributions, and rejects PEP 517 backend paths escaping the source tree via symlinks; `UV_NO_BUILD` documented; `UV_ONLY_BINARY` confirmed not a real env var |
| cargo | 1.83+ | 2026-05-12 | initial author | `cargo-vet`, `cargo-deny`, `cargo-audit` versions pinned in CI examples |
| go | 1.25.10 / 1.26.3 | 2026-05-12 | initial author | Minimum for CVE-2026-42501 fix |
| Yarn | 4.10+ | 2026-08-04 | agent-assisted refresh | `npmMinimalAgeGate` defaults to `"1w"` (cool-off **on** by default); per-package exemptions via `npmPreapprovedPackages` (globs or exact locators); config lives in `.yarnrc.yml` |
| Bun | 1.3+ | 2026-08-04 | agent-assisted refresh | `minimumReleaseAge` defaults to `259200` seconds (3 days, **on** by default); exemptions via `minimumReleaseAgeExcludes`; config in `bunfig.toml`; gate applies at resolution, not to versions already in `bun.lock` ([oven-sh/bun#30525](https://github.com/oven-sh/bun/issues/30525)) |
| Dependabot | n/a (hosted) | 2026-08-04 | agent-assisted refresh | `cooldown.default-days` defaults to **3** since 2026-07-14, version updates only; security updates are exempt; sub-keys `semver-*-days`, `include`, `exclude`; supports pip, uv, and npm |
| Renovate | n/a (hosted) | 2026-08-04 | agent-assisted refresh | `minimumReleaseAge` has no default; `internalChecksFilter` defaults to `strict` |
| osv-scanner | v2.0.2 | 2026-05-23 | agent-assisted refresh | **Needs re-verification.** Pinned in the npm CI recipe; not re-checked on 2026-08-04 because the GitHub releases API was unreachable from the refresh session. Confirm against the [releases page](https://github.com/google/osv-scanner/releases) before the next refresh |
| Claude Code | settings schema as of 2026-08-04 | 2026-08-04 | agent-assisted refresh | Precedence managed > CLI > local > project > user; project `.claude/settings.json` allow rules require workspace trust; `allowManagedHooksOnly`, `allowManagedPermissionRulesOnly`, `disableAllHooks`, `enableAllProjectMcpServers` drive the agent-workspace playbook |
| VS Code | Workspace Trust as of 2026-08-04 | 2026-08-04 | agent-assisted refresh | `task.allowAutomaticTasks` defaults to `off`; automatic tasks never run in an untrusted workspace; `security.workspace.trust.*` settings drive the agent-workspace playbook |

### Procedure

1. Read the release notes for added / renamed / removed config options.
2. Check the env-var documentation page for the canonical names:
   - npm: <https://docs.npmjs.com/cli/v11/configuring-npm/npmrc>
   - pnpm: <https://pnpm.io/settings>
   - pip: <https://pip.pypa.io/en/stable/topics/configuration/>
   - uv: <https://docs.astral.sh/uv/reference/environment/>
   - cargo: <https://doc.rust-lang.org/cargo/reference/config.html>
   - go: <https://pkg.go.dev/cmd/go#hdr-Environment_variables>
   - Claude Code: <https://code.claude.com/docs/en/settings>
   - VS Code Workspace Trust:
     <https://code.visualstudio.com/docs/editing/workspaces/workspace-trust>
3. Update `tests/known-env-vars.txt` if names changed.
4. Run `python3 tests/validate-docs.py`; it must exit 0.
5. Update the playbook if a control’s flag name or unit changed.
6. Bump the row in the Last Verified Against table above with the verifier’s name and
   the date, and refresh the “Last verified” line at the top of `README.md` to match (it
   names the same versions; a stale date there undermines the whole repo).
7. Open an audit-log entry if any control changed semantics (so the change is visible to
   future readers; see
   [`supply-chain-audit-log-template.md`](supply-chain-audit-log-template.md)).

## Maintaining `scripts/audit_workspace.py`

The scanner carries three kinds of knowledge that decay at different rates.
When a new open-time or load-time campaign is verified, update the matching constant and
say which campaign motivated it:

- **`KEYV_HOST_ARTIFACTS` and `KNOWN_PAYLOAD_FILENAMES`** are campaign-specific IOCs and
  age fastest. Add new ones; do not delete old ones, since an old artifact on disk is
  still a finding.
- **`AGENT_INSTRUCTION_FILES` and `AGENT_INSTRUCTION_GLOBS`** track which files agents
  read as trusted context.
  Add a path whenever a widely-used agent introduces one.
- **`PTH_ALLOWLIST_PREFIXES`** is the opposite: it suppresses findings, so additions
  need more care than IOCs do.
  Only add a prefix after confirming the file is generated by a packaging tool rather
  than by a package author, and record why in a comment.

The autostart check’s config paths (`.vscode/tasks.json`, `.claude/settings.json`,
`.codex/hooks.json`, `.devcontainer/`, `.mcp.json`) are hardcoded in
`check_autostart()`; add a path there whenever a widely-used agent or editor introduces
a new repo-committed autostart file, and mirror the addition in
`hardening-agent-workspaces.md` (attack-surface table, triage commands, CI guard) and
`AGENTS.md` rule 6.

Run `python3 tests/test_audit_workspace.py` after any change; it builds synthetic
repositories for each pattern (JSONC with trailing commas, Codex hooks, `.agents/` skill
files with hidden Unicode, executable and non-executable `.pth` lines) and fails if a
check silently stops matching, which is worse than no check.

## Sourcing and Citation Rules

Both doc types share these rules:

- **Cite at least two independent sources** for any incident-specific claim (date,
  affected versions, scale).
- **Prefer primary sources** (project postmortems, vendor security advisories, CISA
  alerts) over aggregator blogs.
- **Quote exact `package@version` strings** for IOCs; vague names like “the qix family”
  are not actionable.
- **Refresh URLs annually**; replace dead links with archive.org snapshots if no live
  source remains.

## Adding a New Ecosystem

To add an ecosystem not yet covered (RubyGems, Hex, NuGet, Composer, Maven, etc.):

1. Use the existing npm pair as the structural template.
   Match section ordering and headings.
2. Create both files in the same commit:
   - `hardening-<ecosystem>.md`
   - `research-<ecosystem>-supply-chain-hardening.md`
3. Update the top-level `README.md` ecosystem index.
4. Confirm both new docs follow `common-doc-guidelines.md` and include the footer.

## Suggested Prompts For Agents

For an incident-driven update to a research doc:

> Update `research-<ecosystem>-supply-chain-hardening.md` for the [name] incident on
> [date]. Follow `self-update-instructions.md` → “Updating Research Docs”.
> Verify with at least two Tier-2 sources from the doc’s feed list before writing.
> Bump the “Last updated” date.

For a tooling-driven update to a hardening doc:

> Update `hardening-<ecosystem>.md` for the new [package-manager] control
> [name/version]. Follow `self-update-instructions.md` → “Updating Hardening
> Guidelines”. Cross-check against the research doc and update there if needed.

For adding a new ecosystem:

> Add hardening and research docs for the [ecosystem] supply chain.
> Follow `self-update-instructions.md` → “Adding a New Ecosystem”.
> Use the npm pair as the structural template; create `hardening-<ecosystem>.md` and
> `research-<ecosystem>-supply-chain-hardening.md` in a single commit.
> Update the top-level README ecosystem index.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
