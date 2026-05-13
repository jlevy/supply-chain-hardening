# Self-Update Instructions

**Last updated:** 2026-05-12

**Author:** Joshua Levy (github.com/jlevy) with agent assistance

Procedures for keeping the docs in this repo current.
Three doc categories require updates on different cadences:

- **Compromised-packages table** (`compromised-packages.md`): canonical cross-ecosystem
  record of named supply-chain incidents.
  Updated whenever a new incident is multi-source verified.
- **Hardening guidelines** (`hardening-<ecosystem>.md`): brief operational action lists.
  Update when configuration recipes change (new env var, new flag, new tool replacing an
  old one).
- **Research docs** (`research-<ecosystem>-supply-chain-hardening.md`): full
  threat-model and per-ecosystem-implementation references.
  Update when an ecosystem-specific control set or mechanism changes, or when there is
  enough mechanism detail to warrant a deep-dive subsection on a particular incident.

When a new incident lands, **update `compromised-packages.md` first**, then add
ecosystem-specific narrative or mechanism detail to the relevant research doc.
Hardening guides only need updates if a new control or shell pattern is involved.

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

`compromised-packages.md` has two sections:

- **Table (Actionable IOCs)**: rows with exact `pkg@version` (or a fully-linked GHSA /
  full-IOC-list URL), dates, and multi-source references.
  Defenders scan against this section.
- **Contextual Incidents (Unverified / Pending Verification)**: campaigns named in
  trusted feeds but missing per-version detail or independent verification.
  Awareness only; no grep-able IOCs.

Add new rows to the **Table** when they meet the bar.
Move rows out of Contextual into the Table when verification is completed, or delete
from Contextual if the campaign turns out to be misattributed.

Procedure:

1. Verify with at least two independent sources from
   [README.md → “Authoritative Sources”](README.md#authoritative-sources) → “Incident
   Reporting Feeds”. Acceptable substitutes: a CISA alert, or a primary maintainer
   postmortem.
2. Append a new row (or rows, one per ecosystem if the campaign hit multiple) to the
   Table. Match the existing column structure exactly: Date, Name, Ecosystem, Scale,
   Affected `pkg@version` (representative), Vector, References.
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
`tests/known-env-vars.txt`. This catches the “`UV_ONLY_BINARY`-class bug” — a
plausibly-named env var that does not actually exist.

When you introduce a new env var in the docs:

1. Add the name to `tests/known-env-vars.txt`. Include a comment with the
   package-manager version that introduced it.
2. If the env var is one that does not work (e.g. you are documenting a common
   misconception), add it to the “Documented-as-not-supported” section of the allow-list
   with a comment explaining the intent.
3. Run `python3 tests/validate-docs.py` locally; it must exit 0.

When a package manager (npm / pnpm / pip / uv / Cargo / Go) releases a major version,
re-verify the env vars it honors:

- Read the release notes for added / renamed / removed config options.
- Update the allow-list accordingly.
- Run the validator.
- Bump the “Last Verified Against” entry for that tool (see
  [MAINTENANCE.md](MAINTENANCE.md)).

## Sourcing And Citation Rules

Both doc types share these rules:

- **Cite at least two independent sources** for any incident-specific claim (date,
  affected versions, scale).
- **Prefer primary sources** (project postmortems, vendor security advisories, CISA
  alerts) over aggregator blogs.
- **Quote exact `package@version` strings** for IOCs; vague names like “the qix family”
  are not actionable.
- **Refresh URLs annually**; replace dead links with archive.org snapshots if no live
  source remains.

## Adding A New Ecosystem

To add an ecosystem not yet covered (RubyGems, Hex, NuGet, Composer, Maven, etc.):

1. Use the existing npm pair as the structural template.
   Match section ordering and headings.
2. Create both files in the same commit:
   - `hardening-<ecosystem>.md`
   - `research-<ecosystem>-supply-chain-hardening.md`
3. Update the top-level `README.md` ecosystem index.
4. Confirm both new docs follow `std-doc-guidelines.md` and include the footer.

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
> Follow `self-update-instructions.md` → “Adding A New Ecosystem”.
> Use the npm pair as the structural template; create `hardening-<ecosystem>.md` and
> `research-<ecosystem>-supply-chain-hardening.md` in a single commit.
> Update the top-level README ecosystem index.

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
