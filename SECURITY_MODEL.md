# Security Model: Layered Defense

**Last updated:** 2026-05-12

**Author:** Joshua Levy (github.com/jlevy) with agent assistance

This repo’s hardening playbooks are one piece of a layered model.
The full stack has six layers; this repo covers L1-L3 and L6 directly, names L5 with a
concrete recipe, and points elsewhere for L4.

## The Layers

| Layer | What | Where |
| --- | --- | --- |
| **L1** Developer defaults | Shell-init env vars (`UV_EXCLUDE_NEWER`, `NPM_CONFIG_BEFORE`, etc.) that harden every `install` from an interactive shell | [guidelines/hardening-npm.md](guidelines/hardening-npm.md), [hardening-pypi.md](guidelines/hardening-pypi.md), [hardening-crates.md](guidelines/hardening-crates.md), [hardening-go.md](guidelines/hardening-go.md) |
| **L2** Project policy | Committed lockfiles, build-script allowlists, registry pins, and workspace-level config | “Step 2” of each playbook; `pnpm-workspace.yaml`, `Cargo.lock`, `uv.lock`, `go.sum` |
| **L3** CI enforcement | Hardening env vars inside CI runners; scanner jobs that fail merge on findings | “CI Enforcement” section of each playbook |
| **L4** Org registry / proxy | Internal mirror with quarantine and delay policy (Artifactory, Nexus, Verdaccio, devpi) | **Out of scope for this repo’s hands-on guidance.** This is the strongest team-level control. Implementations vary by org. Recommended posture; the playbooks describe what the controls should enforce, not how to stand up the mirror. |
| **L5** Untrusted-repo sandbox | Container or namespace-isolated execution for the first run of any unfamiliar third-party repo | [guidelines/untrusted-repo-first-run.md](guidelines/untrusted-repo-first-run.md) |
| **L6** Incident response | Per-incident credential rotation, persistence checks, downgrade, audit-log entry | “If You Have Hits” sections in each playbook; [supply-chain-audit-log-template.md](supply-chain-audit-log-template.md) |

## Reading The Stack

- **L1 alone** is enough for personal workstations and small teams against the
  fast-yanked-incident class of attack.
- **L1 + L2 + L3** is the minimum for any shared codebase: a developer who follows L1
  still cannot single-handedly stop a peer who skips it, but L2’s committed lockfile +
  L3’s CI gate close that gap.
- **L4** is the strongest team-level control because it is the only layer that enforces
  policy across every developer, agent, CI job, and tool that resolves packages.
  If you can stand up a delayed internal mirror, do so; this repo’s scope is the
  per-developer surface area, not the org infrastructure.
- **L5** is critical for AI agents and for anyone routinely cloning third-party repos:
  install scripts, source builds, `build.rs`, proc-macros, and test files all execute
  code with ambient credentials.
- **L6** is the difference between “a malicious package landed on a developer machine”
  and “a malicious package compromised production.”
  Treat the audit log as the canonical record; do not rely on memory.

## How This Repo Maps To The Stack

- **L1**: the four operational hardening guides plus
  [SUPPLY-CHAIN-SECURITY.md](SUPPLY-CHAIN-SECURITY.md) (the portable drop-in).
- **L2**: each playbook’s lockfile / workspace guidance.
- **L3**: each playbook’s “CI Enforcement” section, plus the doc-lint maintenance hooks
  under self-update-instructions.md.
- **L4**: not implemented; mentioned at strategic points and linked here.
  Use Artifactory / Nexus / Verdaccio / devpi or equivalent for npm and PyPI; use a
  controlled `GOPROXY` and crates.io vendoring for Go and Rust.
- **L5**:
  [guidelines/untrusted-repo-first-run.md](guidelines/untrusted-repo-first-run.md) with
  Docker / sandbox-exec / unshare recipes.
- **L6**: per-playbook “If You Have Hits” sections, the audit-log template, and the
  [Compromised Packages](compromised-packages.md) watch list.

## Strict Mode

[`guidelines/strict-mode.md`](guidelines/strict-mode.md) documents the Strict and
Emergency-Exception modes that sit on top of the Balanced default.
Agents and high-risk environments should consult that file before installing anything.

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
