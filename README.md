# Supply Chain Hardening Guidebook

**For AI agents and developers.** Concrete recipes, zero-dep audit scripts, and a
curated watch list of recent compromises across npm, PyPI, crates.io, and Go modules.

**Author:** Joshua Levy (github.com/jlevy) with agent assistance\
**Last updated:** 2026-05-12

## Quick Start

Read the [Safety Note](#safety-note) before applying anything, and validate every recipe
against the [Authoritative Sources](#authoritative-sources).

### Harden A Single Ecosystem

Pick the playbook for the ecosystem you use.
Each is a copy-pasteable Ten-Minute Setup.

| Ecosystem | Playbook |
| --- | --- |
| **npm / Node.js** | [guidelines/hardening-npm.md](guidelines/hardening-npm.md) |
| **PyPI / Python** | [guidelines/hardening-pypi.md](guidelines/hardening-pypi.md) |
| **crates.io / Rust** | [guidelines/hardening-crates.md](guidelines/hardening-crates.md) |
| **Go modules** | [guidelines/hardening-go.md](guidelines/hardening-go.md) |

### Harden All Ecosystems

For an agent or human walking through every ecosystem on a workstation, in order:

1. **Inventory.** Identify which of npm, PyPI, crates.io, Go is installed and used.
   Skip the rest.
2. **Per ecosystem,** open the playbook above and:
   1. Apply the Ten-Minute Setup verbatim, including shell-init and per-platform
      variants.
   2. Run the verification commands.
      Confirm each control reports the expected value.
   3. Run the “Compromise Assessment” commands once to baseline the current state.
   4. Append an entry to the user’s `supply-chain-audit-log.md` (copy from
      [`supply-chain-audit-log-template.md`](supply-chain-audit-log-template.md))
      recording what was set and any hits found.
3. **Cross-check installed packages** against
   [compromised-packages.md](compromised-packages.md) for any `package@version` in the
   watch list.
4. **For npm specifically,** run an OSV-API scan against the global tree:
   `uv run scripts/audit_npm.py`. The script reports `[MALICIOUS]` separately from
   ordinary CVEs and has zero third-party dependencies; see
   [scripts/README.md](scripts/README.md).
5. **If any hit lands,** follow the “If You Have Hits” section in the relevant playbook
   for credential rotation, downgrade, and post-incident steps.

The long-form companions live in [`research/`](research/): threat model, attack
timeline, per-shell setup detail, and severity assessment per ecosystem.

### Drop A Reminder Into Your Own Codebase

[`SUPPLY-CHAIN-SECURITY.md`](SUPPLY-CHAIN-SECURITY.md) is a self-contained, portable
version of the install rules (no newer than 7 days, no unthinking installs, audit after
every install, link back here for detail).
Copy it to your own project root and reference it from your project’s `AGENTS.md` so any
AI agent working in your codebase sees the rules before installing anything.

## For AI Agents

When the user asks you to harden, audit, or assess a package-manager supply chain:

| User Intent | Action |
| --- | --- |
| “Harden my npm setup” | Apply [guidelines/hardening-npm.md](guidelines/hardening-npm.md). Verify with the listed config-get commands. Log to `supply-chain-audit-log.md`. |
| “Harden my PyPI setup” | Apply [guidelines/hardening-pypi.md](guidelines/hardening-pypi.md). Verify, log. |
| “Harden my Rust setup” | Apply [guidelines/hardening-crates.md](guidelines/hardening-crates.md). Verify, log. |
| “Harden my Go setup” | Apply [guidelines/hardening-go.md](guidelines/hardening-go.md). Verify, log. |
| “Harden everything on this machine” | Walk [Harden All Ecosystems](#harden-all-ecosystems) end to end. One audit-log entry per ecosystem. |
| “I just installed X. Am I compromised?” | Start at [compromised-packages.md](compromised-packages.md). For npm, run `uv run scripts/audit_npm.py --packages <pkg@ver>`. For other ecosystems, `osv-scanner` per the playbook. Log findings. |
| “Add a new ecosystem (RubyGems, NuGet, …)” | Follow [self-update-instructions.md](self-update-instructions.md) → “Adding A New Ecosystem”. Cite multiple [authoritative sources](#authoritative-sources). |
| “Update the watch list with a new incident” | Follow [self-update-instructions.md](self-update-instructions.md) → “Updating `compromised-packages.md`”. Verify with at least two [Incident Reporting Feeds](#incident-reporting-feeds-free-public-two-source-verification). |

[`AGENTS.md`](AGENTS.md) carries the same table plus a Safety Rule For Agents block, for
IDEs and agents that auto-load that filename.

## Safety Note

> [!WARNING]
> It is increasingly unsafe to trust even seemingly trustworthy packages or GitHub
> repos. Validate instructions before following them, and validate packages before
> installing them. Have your agent cross-check every recipe in this repo against the
> [Authoritative Sources](#authoritative-sources).

## What This Repo Is (And Is Not)

**This repo is** a methodology resource for agents and humans:

- Per-ecosystem **hardening guides** (the four
  [playbooks above](#harden-a-single-ecosystem)) with copy-pasteable shell and CI
  configuration.
- Per-ecosystem **research docs** in [`research/`](research/) explaining the threat
  model, attack mechanisms, and defensive trade-offs.
- A **layered security model** at [`SECURITY_MODEL.md`](SECURITY_MODEL.md) describing
  how developer defaults, project policy, CI, registry/proxy, sandbox, and incident
  response fit together.
- A **strict-mode reference** at
  [`guidelines/strict-mode.md`](guidelines/strict-mode.md) for agents and high-risk
  environments, plus an
  [untrusted-repo sandbox procedure](guidelines/untrusted-repo-first-run.md) for the
  first run of any third-party code.
- A **curated watch list** at [`compromised-packages.md`](compromised-packages.md) for
  spot-checking installed packages and recognising attack patterns by name.
- A **zero-dependency audit script** at [`scripts/audit_npm.py`](scripts/audit_npm.py)
  and an audit-log template at
  [`supply-chain-audit-log-template.md`](supply-chain-audit-log-template.md).
- A **self-update procedure** at
  [`self-update-instructions.md`](self-update-instructions.md) so any human or agent
  revisiting the repo months later can refresh it predictably.

**This repo is not** a real-time feed of supply-chain compromises.
For that, use the [Authoritative Sources](#authoritative-sources).
The watch list is curated, not exhaustive: notable named incidents that defenders should
recognise, plus enough context to make the hardening guides concrete.

## Why The Hardening Pattern Is Stable Even When The Incident List Changes

The dominant pattern in the 2025-2026 wave is fast-yanked named incidents: malicious
package versions live for minutes to hours before researchers detect them and the
maintainer or registry yanks the bad release (qix, Shai-Hulud 1.0/2.0, Axios, TanStack,
Ultralytics, LiteLLM, Mini Shai-Hulud).

**Core pattern:** delay newly-published versions where the package manager supports it;
otherwise prevent unintentional re-resolution, pin exact versions, verify checksums and
advisories, and require explicit human review for dependency updates.

| Ecosystem | Native release-age gating | Primary protection |
| --- | --- | --- |
| npm / pnpm | yes (`NPM_CONFIG_BEFORE`, `MINIMUM_RELEASE_AGE` on pnpm 10.16+, `MIN_RELEASE_AGE` on npm 11.10+) | release-age delay + disabled install scripts + frozen lockfile |
| PyPI (uv, pip 26.1+, poetry 2.4+, pdm) | yes (`UV_EXCLUDE_NEWER`, `PIP_UPLOADED_PRIOR_TO`, `solver.min-release-age`, `--exclude-newer`) | release-age delay + refuse sdist builds + frozen lockfile with hashes |
| Cargo (crates.io) | no native release-age control | committed `Cargo.lock` + `--locked` + `cargo audit`/`deny`/`vet` |
| Go modules | no native release-age control | committed `go.sum` + `go mod verify` + `govulncheck` + readonly module mode |

For Cargo and Go, “cool-off” can still be implemented through Renovate/Dependabot
policy, internal mirrors, or update wrappers, but it is not a flag the toolchain
exposes. The playbooks translate the per-ecosystem pattern into copy-pasteable commands;
the methodology is what the repo is really about.

**What this neutralises:** the fast-yanked named incidents above.
**What it does not neutralise on its own:** long-lived compromises that survive past the
cool-off window (BoltDB cached in the module proxy for ~3 years; ctx ATO published for
~10 days), lockfiles that already captured a malicious version before the control was
active, and runtime payloads in wheels or proc-macros that execute on import or build
rather than at install time.
Those require additional controls: lockfile review, typo-resistance checks, and the
per-ecosystem build-time controls in the playbooks.

## Maintaining This Repo

All doc-update procedures live in
[`self-update-instructions.md`](self-update-instructions.md).
The package-manager versions the playbooks have been validated against, and the
re-verification procedure for major-version bumps, live in
[`MAINTENANCE.md`](MAINTENANCE.md).
At a glance:

| Document | When To Update | Typical Cadence |
| --- | --- | --- |
| [`compromised-packages.md`](compromised-packages.md) | A notable new supply-chain incident is verified by at least two independent Tier-2 sources, or by CISA | Weeks-to-months |
| Hardening playbooks ([npm](guidelines/hardening-npm.md), [PyPI](guidelines/hardening-pypi.md), [Rust](guidelines/hardening-crates.md), [Go](guidelines/hardening-go.md)) | A package manager ships a relevant new control, or an existing flag or env-var name changes | Months-to-years |
| Research docs (in [`research/`](research/)) | An ecosystem-specific mechanism or control set changes, or a new incident merits a dedicated mechanism deep-dive | Months-to-years |
| [`supply-chain-audit-log-template.md`](supply-chain-audit-log-template.md) | The audit-log entry format evolves | Rarely |

Every doc follows `std-doc-guidelines.md` (author: jlevy), flagged by the footer at the
bottom of each file.
Style for additions: Title Case headings, no spaced em dashes, concrete examples over
generalities, no “talking about talking”, cite primary sources.

## Contributing

Each new ecosystem guide must:

1. Cite multiple independent sources for any named-incident claim.
2. Be specific enough to copy-paste: exact env-var names, exact filenames, exact version
   numbers.
3. Cover macOS, Linux, and Windows where the underlying tooling supports them.
4. End with the standard doc-guidelines footer.
5. Follow the procedure in [`self-update-instructions.md`](self-update-instructions.md).

## Authoritative Sources

Every cross-reference in this repo points back here.
Verify any new incident against at least two of the “Incident Reporting Feeds” before
adding it to [`compromised-packages.md`](compromised-packages.md).

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

## License

[MIT](LICENSE).

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
