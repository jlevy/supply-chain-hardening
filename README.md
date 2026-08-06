# Supply Chain Hardening Guidebook

**For AI agents and developers.** Concrete recipes, zero-dep audit scripts, and a
curated watch list of recent compromises across npm, PyPI, crates.io, and Go modules.

**Author:** Joshua Levy (github.com/jlevy) with agent assistance

## Start Here

Supply-chain payloads no longer share a single execution moment.
**When the payload runs determines which control stops it**, so this table is the
primary map of the repo:

| Trigger | Runs when | Example | What stops it |
| --- | --- | --- | --- |
| **Install-time** | `npm install`, `pip install`, `cargo build` | keyv, Miasma, Shai-Hulud | Cool-off window, disabled install scripts, frozen lockfile: the [ecosystem playbooks](#harden-a-single-ecosystem) |
| **Load-time** | `require()`, `import`, or *any* interpreter start | node-ipc, Hades `.pth` | Cool-off window and [sandboxed first runs](guidelines/untrusted-repo-first-run.md) only |
| **Open-time** | A developer or AI agent *opens* the repo | Miasma/Azure, TrapDoor `CLAUDE.md` | No package-manager control applies. Workspace trust, hook policy, and pre-open triage: the [agent-workspace playbook](guidelines/hardening-agent-workspaces.md) |

The install-side setup is one command per tool you use
([details, verification, and the remaining tools](guidelines/hardening-npm.md#step-0-the-ten-minute-setup)):

```sh
npm config set min-release-age 14 --location=user         # npm 11.10+; days
pnpm config set minimumReleaseAge 20160 --location=user   # pnpm 10.16+; minutes
yarn config set --home npmMinimalAgeGate 20160            # Yarn 4.10+; minutes
export UV_EXCLUDE_NEWER="14 days"                         # uv; put in shell init
```

(Bun needs a per-repo `bunfig.toml`; pip 26.1+ takes `PIP_UPLOADED_PRIOR_TO="P14D"`;
Cargo and Go have no age gate, so commit the lockfile and build `--locked` /
`-mod=readonly`.)

Before opening any repo you did not write:

```sh
uv run scripts/audit_workspace.py ./REPO   # or: python3 scripts/audit_workspace.py ./REPO
```

If you work with AI agents, copy [`SUPPLY-CHAIN-SECURITY.md`](SUPPLY-CHAIN-SECURITY.md)
into your codebase and reference it from your project’s `AGENTS.md`. Everything below is
reference and rationale.

## Choosing Your Path

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
  before any install / build / test / run command, and
  [`guidelines/hardening-agent-workspaces.md`](guidelines/hardening-agent-workspaces.md)
  before *opening* it.
- **Anyone running an AI coding agent or opening third-party repos in an editor:** apply
  [`guidelines/hardening-agent-workspaces.md`](guidelines/hardening-agent-workspaces.md).
- **Machine with publish tokens or production access:** enter Strict mode
  ([`guidelines/strict-mode.md`](guidelines/strict-mode.md)).

### Harden a Single Ecosystem

Pick the playbook for the ecosystem you use.
Each opens with a short, copy-pasteable setup and pushes the edge cases behind an
explicit “only if you need it” boundary.

| Ecosystem | Playbook |
| --- | --- |
| **npm / Node.js** | [guidelines/hardening-npm.md](guidelines/hardening-npm.md) |
| **PyPI / Python** | [guidelines/hardening-pypi.md](guidelines/hardening-pypi.md) |
| **crates.io / Rust** | [guidelines/hardening-crates.md](guidelines/hardening-crates.md) |
| **Go modules** | [guidelines/hardening-go.md](guidelines/hardening-go.md) |
| **CI/CD and publish pipeline** (cross-ecosystem) | [guidelines/hardening-ci-cd.md](guidelines/hardening-ci-cd.md) |
| **AI agent and editor workspaces** (cross-ecosystem) | [guidelines/hardening-agent-workspaces.md](guidelines/hardening-agent-workspaces.md) |

The four per-ecosystem playbooks harden the **install** side.
If you publish packages, or your repo releases via GitHub Actions, also apply the
cross-ecosystem [CI/CD playbook](guidelines/hardening-ci-cd.md): most 2026 incidents
(TanStack, @antv, Megalodon, `durabletask`) compromised the publish pipeline, not a
consumer.

If you use an AI coding agent or open third-party repos in an editor, also apply the
[agent-workspace playbook](guidelines/hardening-agent-workspaces.md).
From April 2026 the attack moved to committed repository config that runs when a folder
is **opened**: `.claude/settings.json` `SessionStart` hooks, `.vscode/tasks.json`
`folderOpen` tasks, and agent instruction files carrying hidden text.
No install happens, so no install-side control in this repo applies.

**Ecosystems not yet covered:** RubyGems / Bundler and Homebrew have no copy-pasteable
playbook here yet. The same methodology applies—commit `Gemfile.lock` and install with
`bundle install --frozen`; use a committed `Brewfile` with `brew bundle`, and disable
Homebrew auto-update (`HOMEBREW_NO_AUTO_UPDATE=1`) for reproducible installs; verify
before upgrading—but neither has a native release-age gate, so treat them like Cargo and
Go (pin, commit the lockfile, review before updating).
Adding a full playbook follows
[self-update-instructions.md](self-update-instructions.md) → “Adding a New Ecosystem”.

### Harden All Ecosystems

For an agent or human walking through every ecosystem on a workstation, in order:

1. **Inventory.** Identify which of npm, PyPI, crates.io, Go is installed and used.
   Skip the rest.
2. **Per ecosystem,** open the playbook above and:
   1. Apply the Setup section verbatim, including shell-init and per-platform variants
      where your situation needs them.
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
5. **Scan for open-time and load-time persistence,** which no lockfile scan will find:
   `uv run scripts/audit_workspace.py --scan-site-packages .` in each repo you have
   opened. It reports planted agent and editor autostart config, hidden Unicode in agent
   instruction files, `.pth` interpreter hooks, and known host persistence.
6. **If any hit lands,** follow the “If You Have Hits” section in the relevant playbook
   for credential rotation, downgrade, and post-incident steps.
   If the hit is host persistence, remove it **before** rotating credentials: the
   2026-08-04 keyv worm’s watcher runs an operator-supplied handler when a stolen token
   stops working.

The long-form companions live in [`research/`](research/): threat model, attack
timeline, per-shell setup detail, and severity assessment per ecosystem.

### Drop a Reminder Into Your Own Codebase

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
| “Harden my AI coding agent / editor” | Apply [guidelines/hardening-agent-workspaces.md](guidelines/hardening-agent-workspaces.md): workspace trust, hook-loading policy, MCP approval, pre-open triage. Verify, log. |
| “Is it safe to open this repo?” | Run `uv run scripts/audit_workspace.py ./REPO` **before** opening it in an editor or pointing an agent at it. Cloning is safe; opening is the risky step. |
| “Harden everything on this machine” | Walk [Harden All Ecosystems](#harden-all-ecosystems) end to end. One audit-log entry per ecosystem. |
| “I just installed X. Am I compromised?” | Start at [compromised-packages.md](compromised-packages.md). For npm, run `uv run scripts/audit_npm.py --packages <pkg@ver>`. For other ecosystems, `osv-scanner` per the playbook. Log findings. |
| “Add a new ecosystem (RubyGems, NuGet, …)” | Follow [self-update-instructions.md](self-update-instructions.md) → “Adding a New Ecosystem”. Cite multiple [authoritative sources](#authoritative-sources). |
| “Update the watch list with a new incident” | Follow [self-update-instructions.md](self-update-instructions.md) → “Updating `compromised-packages.md`”. Verify with at least two [Incident Reporting Feeds](#incident-reporting-feeds-free-public-two-source-verification). |

[`AGENTS.md`](AGENTS.md) carries the same table plus a Safety Rule For Agents block, for
IDEs and agents that auto-load that filename.

## Safety Note

> [!WARNING]
> It is increasingly unsafe to trust even seemingly trustworthy packages or GitHub
> repos. Validate instructions before following them, and validate packages before
> installing them. Have your agent cross-check every recipe in this repo against the
> [Authoritative Sources](#authoritative-sources).

## What This Repo Is (and Is Not)

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
- **Zero-dependency audit scripts:** [`scripts/audit_npm.py`](scripts/audit_npm.py)
  checks installed npm trees against OSV, and
  [`scripts/audit_workspace.py`](scripts/audit_workspace.py) checks a repo and host for
  open-time and load-time persistence.
  Plus an audit-log template at
  [`supply-chain-audit-log-template.md`](supply-chain-audit-log-template.md).
- A **self-update procedure** at
  [`self-update-instructions.md`](self-update-instructions.md) so any human or agent
  revisiting the repo months later can refresh it predictably.

**This repo is not** a real-time feed of supply-chain compromises.
For that, use the [Authoritative Sources](#authoritative-sources).
The watch list is curated, not exhaustive: notable named incidents that defenders should
recognise, plus enough context to make the hardening guides concrete.

## The Layered Model (Where Enforcement Lives)

The repo organises its controls along two orthogonal axes:

- **Trigger class**: *when the payload runs* (install-, load-, or open-time).
  This is the primary lens—the table in [Start Here](#start-here)—because it maps
  one-to-one onto which control stops an attack.
- **Layer**: *where enforcement lives* (developer shell, project config, CI, registry,
  sandbox, incident response).
  Use this second lens to decide where to put a control so that it cannot be bypassed or
  overridden.

Supply-chain hardening is a stack of six layers.
This repo covers L1-L3 and L6 directly, names L5 with a concrete recipe, and points
elsewhere for L4. Everything in the repo maps to one of these layers.

| Layer | What | Where in this repo |
| --- | --- | --- |
| **L1** Developer defaults | Shell-init env vars (`UV_EXCLUDE_NEWER`, `NPM_CONFIG_BEFORE`, etc.) that harden every `install` from an interactive shell, plus your user-level and managed agent/editor settings (workspace trust, hook-loading policy) | The four per-ecosystem playbooks; [`SUPPLY-CHAIN-SECURITY.md`](SUPPLY-CHAIN-SECURITY.md) as the portable drop-in; the settings recipes in the [agent-workspace playbook](guidelines/hardening-agent-workspaces.md) |
| **L2** Project policy | Committed lockfiles, build-script allowlists, registry pins, workspace-level config | “Step 2” of each playbook; `pnpm-workspace.yaml`, `Cargo.lock`, `uv.lock`, `go.sum` |
| **L3** CI enforcement | Hardening env vars inside CI runners; scanner jobs that fail merge on findings; publish-pipeline hardening (read-only PR caches, SHA-pinned actions, runner egress block, OIDC/staged publishing, provenance monitoring) | “CI Enforcement” section of each playbook; the cross-ecosystem [CI/CD playbook](guidelines/hardening-ci-cd.md) |
| **L4** Org registry / proxy | Internal mirror with quarantine and delay policy (Artifactory, Nexus, Verdaccio, devpi) | **Out of scope for hands-on guidance.** Strongest team-level control; implementations vary by org. Use a controlled `GOPROXY` and crates.io vendoring for Go and Rust. |
| **L5** Untrusted-repo sandbox | Container or namespace-isolated execution for the first run of any third-party repo, plus the pre-open triage of repository-supplied agent and editor config | [`guidelines/untrusted-repo-first-run.md`](guidelines/untrusted-repo-first-run.md); the pre-open triage in the [agent-workspace playbook](guidelines/hardening-agent-workspaces.md) and [`scripts/audit_workspace.py`](scripts/audit_workspace.py) |
| **L6** Incident response | Per-incident credential rotation, persistence checks, downgrade, audit-log entry | “If You Have Hits” sections in each playbook; [`supply-chain-audit-log-template.md`](supply-chain-audit-log-template.md) |

How to read the stack:

- **L1 alone** is enough for personal workstations and small teams against the
  fast-yanked-incident class of attack.
- **L1, L2, and L3 together** are the minimum for any shared codebase: L1 protects the
  individual developer, and L2’s committed lockfile plus L3’s CI gate close the gap when
  a peer skips L1.
- **L4** is the strongest team-level control because it is the only layer that enforces
  policy across every developer, agent, CI job, and tool that resolves packages.
  If you can stand up a delayed internal mirror, do so.
  This repo describes what the controls should enforce, not how to stand up the mirror.
- **L5** is critical for AI agents and for anyone routinely cloning third-party repos:
  install scripts, source builds, `build.rs`, proc-macros, and test files all execute
  code with ambient credentials.
- **L6** is the difference between “a malicious package landed on a developer machine”
  and “a malicious package compromised production.”
  Treat the audit log as the record; do not rely on memory.
- **The agent and editor workspace is a surface, not a seventh layer.** Open-time
  attacks are stopped by ordinary L1 controls (your user-level and managed settings,
  which a repository cannot override) and L5 controls (pre-open triage, sandboxed first
  runs) applied at a new surface.
  The [agent-workspace playbook](guidelines/hardening-agent-workspaces.md) is the L1 and
  L5 recipe for that surface.

Mapping the two axes together:

| Trigger | Example | Layer that helps |
| --- | --- | --- |
| Install-time | keyv, Miasma, Shai-Hulud | L1-L4 |
| Load-time | node-ipc, Hades `.pth` | L1 cool-off and L5 sandbox only |
| Open-time | Miasma/Azure, TrapDoor `CLAUDE.md` | L1 agent/editor settings and L5 pre-open triage only |

[`guidelines/strict-mode.md`](guidelines/strict-mode.md) documents the Strict and
Emergency-Exception modes that sit on top of the Balanced default; agents and high-risk
environments should consult that file before installing anything.

## Why the Hardening Pattern Is Stable Even When the Incident List Changes

The dominant pattern in the 2025-2026 wave is fast-yanked named incidents: malicious
package versions live for minutes to hours before researchers detect them and the
maintainer or registry yanks the bad release (qix, Shai-Hulud 1.0/2.0, Axios, TanStack,
Ultralytics, LiteLLM, Mini Shai-Hulud).

**Core pattern:** delay newly-published versions where the package manager supports it;
otherwise prevent unintentional re-resolution, pin exact versions, verify checksums and
advisories, and require explicit human review for dependency updates.

| Ecosystem | Native release-age gating | Primary protection |
| --- | --- | --- |
| npm / pnpm | yes (`NPM_CONFIG_BEFORE`, `MINIMUM_RELEASE_AGE` on pnpm 10.16+, `MIN_RELEASE_AGE` on npm 11.10+) | release-age delay, disabled install scripts, and a frozen lockfile. npm 12 (2026-07-08) blocks dependency lifecycle scripts by default via `allowScripts`, and blocks git and remote-URL dependencies unless `--allow-git` / `--allow-remote` is passed |
| PyPI (uv, pip 26.1+, poetry 2.4+, pdm) | yes (`UV_EXCLUDE_NEWER`, `PIP_UPLOADED_PRIOR_TO`, `solver.min-release-age`, `--exclude-newer`) | release-age delay, refusal of sdist builds, and a frozen lockfile with hashes |
| Cargo (crates.io) | no native release-age control | committed `Cargo.lock`, `--locked`, and `cargo audit`/`deny`/`vet` |
| Go modules | no native release-age control | committed `go.sum`, `go mod verify`, `govulncheck`, and readonly module mode |

**Gate at two layers, not one.** A bot cool-off (Dependabot, Renovate) and a package
manager cool-off gate different events, so neither substitutes for the other.
The bot gates *when an update is proposed*; the package manager gates *what a resolution
may install*. A bot-only window is bypassed by `npm install pkg@latest` typed by hand,
by any CI job that regenerates a lockfile, and by transitive dependencies the bot never
proposed. Renovate’s own documentation recommends configuring the window in both places.
Set both, at the same number.

For Cargo and Go, “cool-off” can still be implemented through Renovate/Dependabot
policy, internal mirrors, or update wrappers, but it is not a flag the toolchain
exposes. The playbooks translate the per-ecosystem pattern into copy-pasteable commands;
the methodology is what the repo is really about.

**What this neutralises:** the fast-yanked named incidents above.

**What it does not neutralise on its own:**

- **Long-lived compromises that outlast the window.** BoltDB and `shopsprint/decimal`
  sat in the Go module proxy for around three years; the `ctx` takeover was live ~10
  days.
- **Lockfiles that already captured a malicious version** before the control was active.
- **Load-time payloads.** Code that runs at `require()` (node-ipc), at `import`
  (TrapDoor’s PyPI packages), or at *every interpreter start* (the June 2026 Hades
  `.pth` wheels). A wheel-only or no-build policy does nothing here, because nothing is
  built and, for `.pth`, nothing is even imported.
- **Open-time payloads.** Committed `.claude/settings.json` hooks, `.vscode/tasks.json`
  `folderOpen` tasks, and agent instruction files carrying zero-width Unicode.
  These arrive through a git repository rather than a registry, so there is no version
  to age and no lockfile entry to review.
  See the [agent-workspace playbook](guidelines/hardening-agent-workspaces.md).
- **Publish-pipeline compromises,** where the malicious version ships from the
  legitimate maintainer’s own CI. By mid-2026 these routinely carry provenance that
  verifies: @antv forged Sigstore attestations at runtime, and Miasma, IronWorm, and the
  keyv worm republished through stolen OIDC credentials.
  A green badge attests to *which pipeline* built a package, not that the pipeline was
  clean.
- **Bring-your-own-runtime payloads.** The keyv and Hades loaders download a standalone
  Bun binary, so “we don’t have Bun installed” is not a control and Node-shaped
  detection misses them.

Those require additional controls: lockfile review, typo-resistance checks, the
per-ecosystem build-time controls in the playbooks, the publish-side controls in the
[CI/CD playbook](guidelines/hardening-ci-cd.md) (OIDC trusted publishing, staged
publishing, runner hardening, provenance monitoring), and the workspace controls in the
[agent-workspace playbook](guidelines/hardening-agent-workspaces.md).

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
| Yarn 4.10+ | `npmMinimalAgeGate: 20160` in `.yarnrc.yml` (minutes; raises the shipped 1-week default) |
| Bun 1.3+ | `minimumReleaseAge = 1209600` in `bunfig.toml` (seconds; raises the shipped 3-day default) |
| uv | `UV_EXCLUDE_NEWER="14 days"`; exempt one package with `exclude-newer-package` |
| pip 26.1+ | `PIP_UPLOADED_PRIOR_TO="P14D"` |
| Cargo / Go | no native gate: committed lockfile, `--locked` / `-mod=readonly`, and human review before re-resolution |

The cool-off applies to your **toolchain** as well as your dependencies.
It is also the only control in this table that does anything about load-time payloads
such as the Hades `.pth` wheels, since those execute without an install script, a source
build, or an import.

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
the evidence base, so treat 14 days as a balanced minimum and lengthen it to taste.

### What The Ecosystems Now Ship By Default

The argument for a cool-off is no longer contrarian.
Between late 2025 and mid-2026 most of the JavaScript toolchain turned one on by
default, and the automated update bots followed.
Verified against vendor documentation on 2026-08-04:

| Tool | Setting | Unit | Default | On by default? |
| --- | --- | --- | --- | --- |
| npm 11.10+ / 12 | `min-release-age` | days | `null` | no |
| pnpm 11+ | `minimumReleaseAge` | minutes | `1440` (1 day) | **yes** |
| Yarn 4.10+ | `npmMinimalAgeGate` | duration | `"1w"` (7 days) | **yes** |
| Bun 1.3+ | `minimumReleaseAge` | seconds | `259200` (3 days) | **yes** |
| uv | `exclude-newer` | date or duration | none | no |
| pip 26.1+ | `--uploaded-prior-to` | ISO 8601 duration | none | no |
| Dependabot | `cooldown.default-days` | days | `3` | **yes** (version updates only) |
| Renovate | `minimumReleaseAge` | duration | none | no |

Three things follow from this table:

- **npm is the outlier in its own ecosystem.** pnpm, Yarn, and Bun all gate by default;
  npm ships `null`. If you use npm, you are the one who has to opt in.
- **Python has no default anywhere.** uv and pip both support a cool-off and neither
  turns it on, so every Python project starts unprotected.
- **The 14-day recommendation is now a modest step past the defaults, not a leap.**
  Yarn’s shipped default is already 7 days, and Dependabot’s is 3.

Defaults do not replace the setting.
A default protects the tool that ships it, on the machine that has it; a committed
policy protects the whole team, and only an explicit value tells a reader which window
you actually chose.

Scope: applies to `dependencies`, `devDependencies` (historically *more* dangerous,
since build tooling runs with full developer privileges), `peerDependencies`, and
`optionalDependencies`; to new installs and upgrades; and to transitive dependencies to
the extent the package manager enforces it.
The cool-off applies to the **whole resolved set, not just the package you named**:
adding or upgrading one dependency can pull in many transitive packages, any of which
may be brand-new, so review the full lockfile diff and confirm the window for *every*
newly added package.
To fix a single violator without re-resolving the whole graph, pin it forward in place
(e.g. `uv lock --upgrade-package <name>==<version>`, `pnpm update <pkg>@<version>`).
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
  Verify it against the [authoritative sources](#authoritative-sources): publisher,
  publish time, and integrity hash.

- **Scope the exception to the one package** using the tool’s own per-package exclude,
  rather than relaxing the global cool-off for the whole dependency graph.
  Every major tool now has one, and a committed entry is reviewable in a way an unset
  environment variable never is:

| Tool | Per-package exclude |
| --- | --- |
| npm 12 | `min-release-age-exclude` (repeatable) |
| pnpm | `minimumReleaseAgeExclude` (name patterns) |
| Yarn 4.10+ | `npmPreapprovedPackages` (globs or exact locators) |
| Bun 1.3+ | `minimumReleaseAgeExcludes` |
| uv | `exclude-newer-package = { pkg = false }` |
| Dependabot | `cooldown.exclude` |

Delete the entry once the version ages past the window.
An exclude left behind turns a one-off exception into a permanent hole.

- Otherwise install it **surgically**, via a direct tarball / wheel URL or a pinned git
  ref, rather than relaxing the gate.
  Each playbook’s “When You Intentionally Need A Fresh Package” step has the
  verify-then-install commands
  ([npm](guidelines/hardening-npm.md#step-4-when-you-intentionally-need-a-fresh-package),
  [PyPI](guidelines/hardening-pypi.md#step-4-when-you-intentionally-need-a-fresh-package);
  [crates](guidelines/hardening-crates.md#step-6-when-you-intentionally-need-an-unvetted-crate)
  and [Go](guidelines/hardening-go.md#verify-a-specific-version-before-adding-it) verify
  before pinning instead, since they have no cool-off to relax).

- Log it in `supply-chain-audit-log.md` with a follow-up to confirm the version was not
  yanked after the fact.

No exception is “trivial” (even a `prettier` patch is in scope): the point of the rule
is that we do not trust ourselves to eyeball which fresh versions are safe.
**Agents never self-approve an exception**; they prepare the record above and a human
signs off. See [`guidelines/strict-mode.md`](guidelines/strict-mode.md) for the full
Emergency-Exception record format.

### Update Discipline: The Safest Update Is the One You Skip

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
| [`compromised-packages.md`](compromised-packages.md) | A notable new supply-chain incident is verified by at least two independent Tier-2 sources, or by CISA; rows older than ~12 months age out to the recognition-only Historical section, so the active list stays capped | Weeks-to-months |
| Hardening playbooks ([npm](guidelines/hardening-npm.md), [PyPI](guidelines/hardening-pypi.md), [Rust](guidelines/hardening-crates.md), [Go](guidelines/hardening-go.md)) | A package manager ships a relevant new control, or an existing flag or env-var name changes | Months-to-years |
| [`guidelines/hardening-agent-workspaces.md`](guidelines/hardening-agent-workspaces.md) | An agent or editor changes its trust model, hook mechanism, or config paths | Months |
| Research docs (in [`research/`](research/)) | An ecosystem-specific mechanism or control set changes, or a new incident merits a dedicated mechanism deep-dive | Months-to-years |
| [`supply-chain-audit-log-template.md`](supply-chain-audit-log-template.md) | The audit-log entry format evolves | Rarely |

Every doc follows `common-doc-guidelines.md` (author: jlevy, upstream
[practical-prose](https://github.com/jlevy/practical-prose)), flagged by the footer at
the bottom of each file and readable with `tbd guidelines common-doc-guidelines`. Style
for additions: Title Case headings, no spaced em dashes, concrete examples over
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
  PyPI coverage; first to publish the IronWorm teardown.
- [SafeDep](https://safedep.io/): registry-backed campaign counts and per-campaign
  tracking pages.
- [Wiz Threat Research](https://www.wiz.io/blog): cloud-credential impact analysis.
- [CISA Alerts](https://www.cisa.gov/news-events/cybersecurity-advisories): US-CERT
  advisories for major incidents.
- Maintainer postmortems (e.g.
  [TanStack postmortem](https://tanstack.com/blog/npm-supply-chain-compromise-postmortem)):
  primary sources when available.

### Commercial (Paid or Mostly-Paid)

[Snyk Vulnerability DB](https://snyk.io/vuln/),
[Sonatype OSS Index](https://ossindex.sonatype.org/),
[JFrog Xray](https://jfrog.com/xray/), [Wiz Threat Intel](https://threats.wiz.io/).

## License

[MIT](LICENSE).

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
