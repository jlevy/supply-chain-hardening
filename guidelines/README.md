# Hardening Guidelines

Brief operational action lists for each ecosystem: minimum hardening setup,
compromise-assessment commands, CI enforcement snippets, audit-log discipline.
Each guide is the action list; deeper background, threat-model context, and per-platform
detail live in the companion research doc in [`../research/`](../research/).

| Ecosystem | Hardening Guidelines |
| --- | --- |
| npm (Node.js) | [hardening-npm.md](hardening-npm.md) |
| PyPI (Python) | [hardening-pypi.md](hardening-pypi.md) |
| crates.io (Rust) | [hardening-crates.md](hardening-crates.md) |
| Go modules | [hardening-go.md](hardening-go.md) |
| CI/CD and publish pipeline (cross-ecosystem) | [hardening-ci-cd.md](hardening-ci-cd.md) |
| AI agent and editor workspaces (cross-ecosystem) | [hardening-agent-workspaces.md](hardening-agent-workspaces.md) |

Two guides are cross-ecosystem.
[hardening-ci-cd.md](hardening-ci-cd.md) hardens the publish side (GitHub Actions,
release tokens, provenance) that the install-side guides do not cover.
[hardening-agent-workspaces.md](hardening-agent-workspaces.md) covers payloads that run
when a repository is *opened* rather than installed, where no package-manager control
applies.

Two further guides are not ecosystem-specific: [strict-mode.md](strict-mode.md) defines
the Strict and Emergency-Exception modes above the Balanced default, and
[untrusted-repo-first-run.md](untrusted-repo-first-run.md) is the sandbox procedure for
the first run of any third-party code.

Update procedure: [`../self-update-instructions.md`](../self-update-instructions.md) →
“Updating Hardening Guidelines”.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
