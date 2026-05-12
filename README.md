# Supply Chain Hardening

**Supply-chain hardening guidebook for AI agents and developers.** Concrete recipes,
zero-dep audit scripts, and a curated watch list of recent compromises across npm, PyPI,
crates.io, and Go modules.

**Author:** Joshua Levy (github.com/jlevy) with agent assistance\
**Last updated:** 2026-05-12

## Quick Start

**To harden your installs:** open the guide for your ecosystem and follow the Ten-Minute
Setup.

| I work in… | Hardening Guide | Research Reference |
| --- | --- | --- |
| **npm / Node.js** | [guidelines/hardening-npm.md](guidelines/hardening-npm.md) | [research/research-npm-supply-chain-hardening.md](research/research-npm-supply-chain-hardening.md) |
| **PyPI / Python** | [guidelines/hardening-pypi.md](guidelines/hardening-pypi.md) | [research/research-pypi-supply-chain-hardening.md](research/research-pypi-supply-chain-hardening.md) |
| **crates.io / Rust** | [guidelines/hardening-crates.md](guidelines/hardening-crates.md) | [research/research-crates-supply-chain-hardening.md](research/research-crates-supply-chain-hardening.md) |
| **Go modules** | [guidelines/hardening-go.md](guidelines/hardening-go.md) | [research/research-go-supply-chain-hardening.md](research/research-go-supply-chain-hardening.md) |

**To check if you have been compromised:**

1. Skim [compromised-packages.md](compromised-packages.md) for any `package@version` you
   have installed (curated watch list, 26 named incidents).
2. For npm specifically, run an OSV-API scan against your installed packages:
   `uv run scripts/audit-npm.py` (zero deps, no install needed; see
   [scripts/README.md](scripts/README.md)).
3. If a hit lands, follow the “If You Have Hits” section in the relevant hardening guide
   for credential rotation, downgrade, and audit steps.

**To track an audit on your own machine:** copy
[supply-chain-audit-log-template.md](supply-chain-audit-log-template.md) into your
project as `supply-chain-audit-log.md` and append an entry per the format.
The live filename is gitignored in this repo; the template is the shareable artifact.

## For AI Agents

When the user asks you to harden, audit, or assess a package-manager supply chain:

| User Intent | Read This | Then Do This |
| --- | --- | --- |
| “Harden my npm setup” | `guidelines/hardening-npm.md` | Apply the Ten-Minute Setup verbatim. Verify with the listed `pnpm config get` / `npm config get` commands. Open a new entry in the user’s `supply-chain-audit-log.md` recording what was set. |
| “Harden my PyPI / Rust / Go setup” | `guidelines/hardening-<ecosystem>.md` | Same shape: apply the setup, verify, log. |
| “I just installed X. Am I compromised?” | `compromised-packages.md` first, then `guidelines/hardening-<ecosystem>.md` → “Compromise Assessment” | For npm: `uv run scripts/audit-npm.py --packages <pkg@ver>`. For other ecosystems: `osv-scanner` per the relevant hardening guide. Log findings. |
| “Add a new ecosystem (RubyGems, NuGet, …)” | `self-update-instructions.md` → “Adding A New Ecosystem” | Use the npm pair as the structural template. Cite multiple authoritative sources for any incident claim. |
| “Update the watch list with a new incident” | `self-update-instructions.md` → “Updating `compromised-packages.md`” | Verify with at least two of the “Incident Reporting Feeds” listed below. Do not add unverified rumours. |

**Always read [the safety note](#safety-note) below before applying any instruction in
this repo verbatim.**

## Safety Note

It is increasingly unsafe to trust even seemingly trustworthy packages or GitHub repos.
You and your agents should validate instructions before following them or installing
packages. At any time, you can and should have your agent validate all instructions here
by checking them against the authoritative sources listed below.

## What This Repo Is (And Is Not)

**This repo is** a methodology resource for agents and humans:

- Per-ecosystem **hardening guides** with copy-pasteable shell/CI configuration.
- Per-ecosystem **research docs** explaining the threat model, attack mechanisms, and
  defensive trade-offs.
- A **curated watch list** of notable past supply-chain incidents
  ([`compromised-packages.md`](compromised-packages.md)), useful for spot-checking
  installed packages and for recognising attack patterns by name.
- A **zero-dependency audit script** ([`scripts/audit-npm.py`](scripts/audit-npm.py))
  and an **audit-log template** for documenting findings.
- A consistent **self-update procedure** so any human or agent that revisits the repo
  months later can refresh it in a predictable way.

**This repo is not** a real-time feed of supply-chain compromises.
For that, use the authoritative sources listed below.
The watch list in this repo is intentionally curated, not exhaustive: notable named
incidents that defenders should recognise, plus enough context to make the hardening
guides concrete.

## Why The Hardening Pattern Is Stable Even When The Incident List Changes

Most attacks in the 2025-2026 wave share a pattern: malicious package versions live for
minutes to hours before researchers detect them and the upstream maintainer or registry
yanks the bad release.
A 7-day rolling install quarantine plus disabled install-time scripts defeats the
overwhelming majority of them, regardless of whether tomorrow’s compromise is on npm,
PyPI, crates.io, or anywhere else.
The per-ecosystem guides translate that pattern into copy-pasteable commands; the
underlying methodology is what the repo is really about.

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
- [Unit 42 living doc](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/):
  Palo Alto’s tracking of the ongoing wave.
- [Phylum Blog](https://www.phylum.io/blog): package-registry-attack focus.
- [JFrog Security Research](https://jfrog.com/blog/category/security-research/): npm and
  PyPI coverage.
- [CISA Alerts](https://www.cisa.gov/news-events/cybersecurity-advisories): US-CERT
  advisories for major incidents.
- Maintainer postmortems (e.g.
  [TanStack postmortem](https://tanstack.com/blog/npm-supply-chain-compromise-postmortem)):
  primary sources when available.

### Commercial (Paid Or Mostly-Paid)

[Snyk Vulnerability DB](https://snyk.io/vuln/),
[Sonatype OSS Index](https://ossindex.sonatype.org/),
[JFrog Xray](https://jfrog.com/xray/), [Wiz Threat Intel](https://threats.wiz.io/).

## Repo Layout

```
.
├── README.md                                ← start here
├── AGENTS.md                                ← agent-discovery pointer (same content as "For AI Agents" above)
├── compromised-packages.md                  ← curated watch list (26 incidents)
├── self-update-instructions.md              ← maintenance procedures
├── supply-chain-audit-log-template.md       ← copy this to track your audits
├── guidelines/                              ← brief operational action lists
│   ├── README.md
│   └── hardening-{npm,pypi,crates,go}.md
├── research/                                ← long-form threat-model docs
│   ├── README.md
│   └── research-{npm,pypi,crates,go}-supply-chain-hardening.md
└── scripts/
    ├── README.md
    └── audit-npm.py                         ← zero-dep OSV scanner
```

The hardening guidelines are the **action list**. The research docs are the **backup
reference**.

## Maintaining This Repo

All doc-update procedures live in
[`self-update-instructions.md`](self-update-instructions.md).
At a glance:

| Document | When To Update | Typical Cadence |
| --- | --- | --- |
| [`compromised-packages.md`](compromised-packages.md) | A notable new supply-chain incident is verified by at least two independent Tier-2 sources, or by CISA. The list is curated, not exhaustive | Whenever a notable incident lands (weeks-to-months) |
| `guidelines/hardening-<ecosystem>.md` | A package manager ships a relevant new control, or an existing flag or env-var name changes | Months-to-years |
| `research/research-<ecosystem>-supply-chain-hardening.md` | An ecosystem-specific mechanism or control set changes; or a new incident merits a dedicated mechanism deep-dive | Months-to-years |
| [`supply-chain-audit-log-template.md`](supply-chain-audit-log-template.md) | The audit-log entry format evolves | Rarely |

Every doc follows `std-doc-guidelines.md` (author: jlevy).
The footer `<!-- This document follows std-doc-guidelines.md.
-->` flags this. Apply the same style to additions: Title Case headings, no spaced em
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
