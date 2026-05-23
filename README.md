# Supply Chain Hardening Guidebook

**For AI agents and developers.** Concrete recipes, zero-dep audit scripts, and a
curated watch list of recent compromises across npm, PyPI, crates.io, and Go modules.

**Author:** Joshua Levy (github.com/jlevy) with agent assistance\
**Last updated:** 2026-05-23

## Quick Start

Read the [Safety Note](#safety-note) before applying anything, and validate every recipe
against the [Authoritative Sources](#authoritative-sources).

### Which Path Do I Follow?

- **Consumer-only repo** (you install dependencies, you do not publish packages): apply
  the ecosystem [playbook](#harden-a-single-ecosystem), commit lockfiles, and add a CI
  scanner gate.
- **Repo that publishes packages or releases via GitHub Actions:** apply
  [`guidelines/hardening-ci-cd.md`](guidelines/hardening-ci-cd.md) first, then the
  ecosystem playbook. The minimum GitHub Actions defaults: top-level
  `permissions: contents: read`; no `pull_request_target` workflow that checks out PR
  head code; restore-only cache on PRs (and avoid implicit cache saves from setup
  actions); SHA-pin actions; OIDC trusted publishing plus npm staged publishing; publish
  job behind a GitHub Environment with required reviewers.
- **Agent working in an untrusted repo:** follow
  [`guidelines/untrusted-repo-first-run.md`](guidelines/untrusted-repo-first-run.md)
  before any install / build / test / run command.
- **Machine with publish tokens or production access:** enter Strict mode
  ([`guidelines/strict-mode.md`](guidelines/strict-mode.md)).

### Harden A Single Ecosystem

Pick the playbook for the ecosystem you use.
Each is a copy-pasteable Ten-Minute Setup.

| Ecosystem | Playbook |
| --- | --- |
| **npm / Node.js** | [guidelines/hardening-npm.md](guidelines/hardening-npm.md) |
| **PyPI / Python** | [guidelines/hardening-pypi.md](guidelines/hardening-pypi.md) |
| **crates.io / Rust** | [guidelines/hardening-crates.md](guidelines/hardening-crates.md) |
| **Go modules** | [guidelines/hardening-go.md](guidelines/hardening-go.md) |
| **CI/CD and publish pipeline** (cross-ecosystem) | [guidelines/hardening-ci-cd.md](guidelines/hardening-ci-cd.md) |

The four per-ecosystem playbooks harden the **install** side.
If you publish packages, or your repo releases via GitHub Actions, also apply the
cross-ecosystem [CI/CD playbook](guidelines/hardening-ci-cd.md): most 2026 incidents
(TanStack, @antv, Megalodon, `durabletask`) compromised the publish pipeline, not a
consumer.

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
version of the install rules (no newer than 14 days, no unthinking installs, audit after
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
| “Harden my CI / release pipeline” or “We publish packages” | Apply [guidelines/hardening-ci-cd.md](guidelines/hardening-ci-cd.md): read-only PR caches, SHA-pinned actions, runner egress block, OIDC/staged publishing, provenance monitoring. |
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
  configuration, plus a cross-ecosystem
  [CI/CD and publish-pipeline guide](guidelines/hardening-ci-cd.md) for the GitHub
  Actions and release-token vectors behind the 2026 worm campaigns.
- Per-ecosystem **research docs** in [`research/`](research/) explaining the threat
  model, attack mechanisms, and defensive trade-offs.
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

## The Layered Model

Supply-chain hardening is a stack of six layers.
This repo covers L1-L3 and L6 directly, names L5 with a concrete recipe, and points
elsewhere for L4. Everything in the repo maps to one of these layers.

| Layer | What | Where in this repo |
| --- | --- | --- |
| **L1** Developer defaults | Shell-init env vars (`UV_EXCLUDE_NEWER`, `NPM_CONFIG_BEFORE`, etc.) that harden every `install` from an interactive shell | The four per-ecosystem playbooks; [`SUPPLY-CHAIN-SECURITY.md`](SUPPLY-CHAIN-SECURITY.md) as the portable drop-in |
| **L2** Project policy | Committed lockfiles, build-script allowlists, registry pins, workspace-level config | “Step 2” of each playbook; `pnpm-workspace.yaml`, `Cargo.lock`, `uv.lock`, `go.sum` |
| **L3** CI enforcement | Hardening env vars inside CI runners; scanner jobs that fail merge on findings; publish-pipeline hardening (read-only PR caches, SHA-pinned actions, runner egress block, OIDC/staged publishing, provenance monitoring) | “CI Enforcement” section of each playbook; the cross-ecosystem [CI/CD playbook](guidelines/hardening-ci-cd.md) |
| **L4** Org registry / proxy | Internal mirror with quarantine and delay policy (Artifactory, Nexus, Verdaccio, devpi) | **Out of scope for hands-on guidance.** Strongest team-level control; implementations vary by org. Use a controlled `GOPROXY` and crates.io vendoring for Go and Rust. |
| **L5** Untrusted-repo sandbox | Container or namespace-isolated execution for the first run of any third-party repo | [`guidelines/untrusted-repo-first-run.md`](guidelines/untrusted-repo-first-run.md) |
| **L6** Incident response | Per-incident credential rotation, persistence checks, downgrade, audit-log entry | “If You Have Hits” sections in each playbook; [`supply-chain-audit-log-template.md`](supply-chain-audit-log-template.md) |

How to read the stack:

- **L1 alone** is enough for personal workstations and small teams against the
  fast-yanked-incident class of attack.
- **L1 + L2 + L3** is the minimum for any shared codebase: L1 protects the individual
  developer, L2’s committed lockfile + L3’s CI gate close the gap when a peer skips L1.
- **L4** is the strongest team-level control because it is the only layer that enforces
  policy across every developer, agent, CI job, and tool that resolves packages.
  If you can stand up a delayed internal mirror, do so.
  This repo describes what the controls should enforce, not how to stand up the mirror.
- **L5** is critical for AI agents and for anyone routinely cloning third-party repos:
  install scripts, source builds, `build.rs`, proc-macros, and test files all execute
  code with ambient credentials.
- **L6** is the difference between “a malicious package landed on a developer machine”
  and “a malicious package compromised production.”
  Treat the audit log as the canonical record; do not rely on memory.

[`guidelines/strict-mode.md`](guidelines/strict-mode.md) documents the Strict and
Emergency-Exception modes that sit on top of the Balanced default; agents and high-risk
environments should consult that file before installing anything.

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
cool-off window (BoltDB and `shopsprint/decimal` cached in the Go module proxy for ~3
years; ctx ATO published for ~10 days), lockfiles that already captured a malicious
version before the control was active, runtime payloads in wheels or proc-macros (and
`require()`-time payloads like node-ipc) that execute on import or build rather than at
install time, and **publish-pipeline compromises** where the malicious version ships
from the legitimate maintainer’s own CI, sometimes carrying valid (forged) provenance,
as in the May 2026 @antv worm.
Those require additional controls: lockfile review, typo-resistance checks, the
per-ecosystem build-time controls in the playbooks, and the publish-side controls in the
[CI/CD playbook](guidelines/hardening-ci-cd.md) (OIDC trusted publishing, staged
publishing, runner hardening, provenance monitoring).

## The Default Policy: A 14-Day Cool-Off

**Never install or upgrade to a package version less than 14 days old, unless a
documented exception applies.** This is the single default this repo recommends across
every ecosystem.
The control differs by tool (the per-ecosystem playbooks have the exact,
version-specific recipes and verification):

| Tool | 14-day control |
| --- | --- |
| npm (any) | `NPM_CONFIG_BEFORE=<now-minus-14d>` |
| npm 11.10+ | `NPM_CONFIG_MIN_RELEASE_AGE=14` (days) |
| pnpm 10.16-10.x | `NPM_CONFIG_MINIMUM_RELEASE_AGE=20160` (minutes) |
| pnpm 11+ | `minimumReleaseAge: 20160` in `pnpm-workspace.yaml` (pnpm 11 ignores `NPM_CONFIG_*`) |
| uv | `UV_EXCLUDE_NEWER="14 days"` |
| pip 26.1+ | `PIP_UPLOADED_PRIOR_TO="P14D"` |
| Cargo / Go | no native gate: committed lockfile + `--locked` / `-mod=readonly` + human review before re-resolution |

**The general principle.** A cool-off works because the registry and researchers detect
and yank malicious versions while legitimate versions keep accruing age.
So the *only* thing the window length trades off is detection coverage against how stale
your dependencies are: a longer window catches more of the slow-detection tail, and its
only cost is waiting longer for legitimate updates.
The benefit curve flattens out (most incidents die in hours to a few days), while the
staleness cost grows roughly linearly, so there is a knee in the curve rather than a
single magic number.
**14 days is the recommended floor**, not a ceiling.

Why at least 14 days:

- **Detection window.** Most malicious publishes are reported and yanked within 3-7
  days; 14 days is a generous buffer past that median.
- **It covers the realistic tail, not just the fast cases.** Many incidents die in
  minutes (Bitwarden ~93 min, @antv ~22 min), but the value of a cool-off is set by the
  *slowest*-detected incidents.
  The `ctx` PyPI takeover was malicious for ~10 days.
  A 7-day window misses it; a 14-day window catches it.
- **Patch bumps are where malware hides.** Many compromises arrive as a `1.2.3 -> 1.2.4`
  patch. A trailing-age window neutralises the whole “fresh patch is malicious” class
  regardless of which dependency moved.
- **The cost is asymmetric.** Waiting 14 days on a routine upgrade is essentially free;
  the only real cost is an urgent security patch, which the exception process handles.

**Pick a larger number if you can.** Nothing here caps the window at 14: a 30-, 60-, or
90-day cool-off is strictly safer, and high-risk environments (machines with publish
tokens or production access) should go higher.
The “Live X hours” timings in [`compromised-packages.md`](compromised-packages.md) are
the evidence base, and pnpm 11 ships a 1-day default (`minimumReleaseAge: 1440`) as the
ecosystem’s own floor, so treat 14 days as a balanced minimum and lengthen it to taste.

Scope: applies to `dependencies`, `devDependencies` (historically *more* dangerous,
since build tooling runs with full developer privileges), `peerDependencies`, and
`optionalDependencies`; to new installs and upgrades; and to transitive dependencies to
the extent the package manager enforces it.
Pins resolved before adopting the policy are grandfathered until their next planned
upgrade.

### The Exception Process

When a version inside the 14-day window is genuinely needed (for example a CVE patch
published yesterday that fixes a vulnerability you are exposed to), take the exception
*explicitly and on the record*:

- State the reason in the commit message or PR description: the CVE ID (or vulnerability
  description if none yet), a link to the upstream release notes, and a `Reviewed-by:`
  sign-off line.
- Pin the exact `package@version`, not a range.
  Verify it against the [authoritative sources](#authoritative-sources).
- Log it in `supply-chain-audit-log.md` with a follow-up to confirm the version was not
  yanked after the fact.

No exception is “trivial” (even a `prettier` patch is in scope): the point of the rule
is that we do not trust ourselves to eyeball which fresh versions are safe.
**Agents never self-approve an exception**; they prepare the record above and a human
signs off. See [`guidelines/strict-mode.md`](guidelines/strict-mode.md) for the full
Emergency-Exception record format.

### Update Discipline: The Safest Update Is The One You Skip

A cool-off decides *when* to take an update.
The prior question is *whether* to update at all.
Each update is fresh attack surface, and updating has repeatedly proven riskier than the
latent bugs it fixes.
Mitchell Hashimoto (HashiCorp, Ghostty) puts the strong form of this well:

> Fork your dependencies, trim them to only your use case, never update unless it breaks
> for your users. [...] updating is way riskier than latent bugs (which can be tracked
> and CVEs monitored).
> If you are updating a dependency, it’s on you to analyze every single commit in the
> full transitive set of dependencies.
> If you don’t see anything compelling, don’t update!
> [...] Don’t update for the sake of it.

This is one influential school, and the absolutist version trades supply-chain risk for
the risk of *not* applying a needed security fix.
The balance this repo recommends:

- **Default to not updating.** Don’t bump a dependency without a concrete reason ("show
  me the commit we need"). Minimise the dependency count, and prefer vendoring or
  pinning for small, stable libraries.
- **Monitor CVEs so the exception is data-driven.** The post-install audit commands
  (`npm audit`, `pip-audit`, `cargo audit`, `govulncheck`) and the IOC feeds are how you
  learn a real security update is needed, which is exactly when the 14-day exception
  applies.
- **When you do update, review the change set,** not just the version number, and then
  still wait out the 14-day window unless it is a security exception.

## Maintaining This Repo

All doc-update procedures live in
[`self-update-instructions.md`](self-update-instructions.md), including the table of
package-manager versions the playbooks have been validated against and the
re-verification procedure for major-version bumps.
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
