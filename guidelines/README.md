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

The CI/CD guide is cross-ecosystem: it hardens the publish side (GitHub Actions, release
tokens, provenance) that the per-ecosystem install-side guides do not cover.

Update procedure: [`../self-update-instructions.md`](../self-update-instructions.md) →
“Updating Hardening Guidelines”.

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
