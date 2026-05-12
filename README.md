# Supply Chain Hardening

**Supply-chain hardening guidebook for AI agents and developers.** Concrete recipes,
zero-dep audit scripts, and a curated watch list of recent compromises across npm, PyPI,
crates.io, and Go modules.

**Author:** Joshua Levy (github.com/jlevy) with agent assistance\
**Last updated:** 2026-05-12

## What This Repo Is (And Is Not)

**This repo is** a methodology resource for **agents and humans**:

- Per-ecosystem **hardening guides** with copy-pasteable shell/CI configuration.
- Per-ecosystem **research docs** explaining the threat model, attack mechanisms, and
  defensive trade-offs.
- A **curated watch list** of notable past supply-chain incidents
  (`compromised-packages.md`), useful for spot-checking installed packages and for
  recognising attack patterns by name.
- A **zero-dependency audit script** (`scripts/audit-npm.py`) and an **audit-log
  template** for documenting findings.
- A consistent **self-update procedure** so any human or agent that revisits the repo
  months later can refresh it in a predictable way.

**Important:** It is increasingly unsafe to trust even seemingly trustworth packages or
GitHub repos. You and yuour agents should validate instructions before following them or
installing packages.
At any time, you can can and should have your agent validate all instructions here by
checking them against other trusted sources.

**This repo is not** a real-time feed of supply-chain compromises.
For that, use the authoritative sources listed below.
The watch list in this repo is intentionally curated, not exhaustive: notable named
incidents that defenders should recognise, plus enough context to make the hardening
guides concrete.

## Authoritative Sources

Every cross-reference in this repo points back here.
Verify any new incident against at least two of the “Incident Reporting Feeds” before
adding it to `compromised-packages.md`.

### Per-Ecosystem Vulnerability Databases (System Of Record)

- **npm:** [OSV.dev npm feed](https://osv.dev/list?ecosystem=npm),
  [GHSA npm filter](https://github.com/advisories?query=type%3Areviewed+ecosystem%3Anpm),
  `npm audit`.
- **PyPI:** [OSV.dev PyPI feed](https://osv.dev/list?ecosystem=PyPI),
  [PyPA Advisory DB](https://github.com/pypa/advisory-database),
  [GHSA PyPI filter](https://github.com/advisories?query=type%3Areviewed+ecosystem%3Apip),
  `pip-audit`.
- **crates.io:** [RustSec Advisory DB](https://rustsec.org/),
  [OSV.dev crates.io feed](https://osv.dev/list?ecosystem=crates.io),
  [GHSA Rust filter](https://github.com/advisories?query=type%3Areviewed+ecosystem%3Arust),
  `cargo audit`.
- **Go modules:** [Go Vulnerability DB](https://pkg.go.dev/vuln/)
  ([machine-readable](https://vuln.go.dev/)),
  [OSV.dev Go feed](https://osv.dev/list?ecosystem=Go),
  [GHSA Go filter](https://github.com/advisories?query=type%3Areviewed+ecosystem%3Ago),
  `govulncheck`.
- **Cross-ecosystem programmatic:** [OSV.dev API](https://google.github.io/osv.dev/api/)
  (`POST /v1/query` for one package, `POST /v1/querybatch` for up to 1000),
  [deps.dev API](https://deps.dev/).

### Incident Reporting Feeds (Free, Public, Two-Source Verification)

- [Aikido Intel](https://intel.aikido.dev): live tracker with per-incident package
  lists.
- [StepSecurity Blog](https://www.stepsecurity.io/blog): often the first public
  detector; publishes file-level IOCs.
- [Socket Security Blog](https://socket.dev/blog): sandboxed-execution analysis.
- [Datadog Security Labs](https://securitylabs.datadoghq.com/): worm-pattern technical
  deep-dives.
- [ReversingLabs Blog](https://www.reversinglabs.com/blog): malware analysis with
  file-level IOCs.
- [Unit 42 living doc](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/)
  : Palo Alto’s tracking of the ongoing wave.
- [Phylum Blog](https://www.phylum.io/blog): package-registry-attack focus.
- [JFrog Security Research](https://jfrog.com/blog/category/security-research/): npm and
  PyPI coverage.
- [CISA Alerts](https://www.cisa.gov/news-events/cybersecurity-advisories): US-CERT
  advisories for major incidents.
- Maintainer postmortems (e.g.
  [TanStack postmortem](https://tanstack.com/blog/npm-supply-chain-compromise-postmortem))
  : primary sources when available.

### Commercial (Paid Or Mostly-Paid)

[Snyk Vulnerability DB](https://snyk.io/vuln/),
[Sonatype OSS Index](https://ossindex.sonatype.org/),
[JFrog Xray](https://jfrog.com/xray/), [Wiz Threat Intel](https://threats.wiz.io/).

## Why The Hardening Pattern Is Stable Even When The Incident List Changes

Most attacks in the 2025-2026 wave share a pattern: malicious package versions live for
minutes to hours before researchers detect them and the upstream maintainer or registry
yanks the bad release.
A 7-day rolling install quarantine plus disabled install-time scripts defeats the
overwhelming majority of them, regardless of whether tomorrow’s compromise is on npm,
PyPI, crates.io, or anywhere else.
The per-ecosystem guides translate that pattern into copy-pasteable commands; the
underlying methodology is what the repo is really about.

## Layout

Two documents per ecosystem:

- **Hardening guidelines** (`hardening-<ecosystem>.md`): minimum hardening steps,
  compromise-assessment commands, and CI enforcement snippets.
  Brief by design.
- **Research doc** (`research-<ecosystem>-supply-chain-hardening.md`): full threat
  model, attack timeline, per-platform and per-shell setup, IOC feeds, and scanning-tool
  comparisons.

The hardening guidelines doc is the action list.
The research doc is the backup reference.
Both doc categories share a common update procedure documented in
[`self-update-instructions.md`](self-update-instructions.md).

Supporting artifacts at the repo root:

- [`compromised-packages.md`](compromised-packages.md): curated table of notable named
  supply-chain incidents across ecosystems, intended as a quick-reference watch list.
  Not exhaustive: routine typosquats and low-impact incidents are omitted by design, and
  the comprehensive feeds are OSV.dev, GHSA, and the per-ecosystem advisory databases.
  Per-ecosystem hardening and research docs link here rather than duplicating the table.
- [`scripts/`](scripts/): zero-dependency Python tools for auditing installed packages.
  See [`scripts/README.md`](scripts/README.md).
  The first script (`audit-npm.py`) scans a node_modules tree against the OSV
  vulnerability database; more will be added per ecosystem.
- [`supply-chain-audit-log-template.md`](supply-chain-audit-log-template.md): template
  for the audit-log discipline recommended in the hardening guidelines.
  Copy this file to your own repo or machine and rename to `supply-chain-audit-log.md`;
  that filename is gitignored at this repo’s root because audit logs typically contain
  machine-specific paths.
- [`Makefile`](Makefile): `make format` auto-formats all Markdown with
  `uvx flowmark-rs@0.2.6` (pinned for supply-chain safety).

## Ecosystems

| Ecosystem | Hardening Guidelines | Research Doc | Status |
| --- | --- | --- | --- |
| npm (Node.js) | [hardening-npm.md](guidelines/hardening-npm.md) | [research-npm-supply-chain-hardening.md](research/research-npm-supply-chain-hardening.md) | Complete |
| PyPI (Python) | [hardening-pypi.md](guidelines/hardening-pypi.md) | [research-pypi-supply-chain-hardening.md](research/research-pypi-supply-chain-hardening.md) | Complete |
| crates.io (Rust) | [hardening-crates.md](guidelines/hardening-crates.md) | [research-crates-supply-chain-hardening.md](research/research-crates-supply-chain-hardening.md) | Complete |
| Go modules | [hardening-go.md](guidelines/hardening-go.md) | [research-go-supply-chain-hardening.md](research/research-go-supply-chain-hardening.md) | Complete |

The npm pair is the structural template.
Adding another ecosystem (RubyGems, NuGet, etc.)
follows the procedure in `self-update-instructions.md` → “Adding A New Ecosystem”.

## Maintaining This Repo

All doc-update procedures live in
[`self-update-instructions.md`](self-update-instructions.md).
At a glance:

| Document | When To Update | Typical Cadence |
| --- | --- | --- |
| [`compromised-packages.md`](compromised-packages.md) | A notable new supply-chain incident is verified by at least two independent Tier-2 sources, or by CISA. The list is curated, not exhaustive | Whenever a notable incident lands (weeks-to-months) |
| [`hardening-<ecosystem>.md`](guidelines/hardening-npm.md) | A package manager ships a relevant new control, or an existing flag or env-var name changes | Months-to-years |
| [`research-<ecosystem>-supply-chain-hardening.md`](research/research-npm-supply-chain-hardening.md) | An ecosystem-specific mechanism or control set changes; or a new incident merits a dedicated mechanism deep-dive | Months-to-years |
| [`supply-chain-audit-log-template.md`](supply-chain-audit-log-template.md) | The audit-log entry format evolves | Rarely |

Every doc in this repo follows `std-doc-guidelines.md` (author: jlevy).
The standard footer at the bottom of each file (`<!-- This document follows
std-doc-guidelines.md.
-->`) flags this. Apply the same style to additions: Title Case headings, no spaced em
dashes, concrete examples over generalities, no “talking about talking”, cite primary
sources.

## Contributing

Each new ecosystem guide must:

1. Cite multiple independent sources for any named-incident claim.
2. Be specific enough to copy-paste: exact env-var names, exact filenames, exact version
   numbers.
3. Cover macOS, Linux, and Windows where the underlying tooling supports them.
4. End with the standard doc-guidelines footer.
5. Follow the procedure in [`self-update-instructions.md`](self-update-instructions.md).

## License

[MIT](LICENSE).

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
