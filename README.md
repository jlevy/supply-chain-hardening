# Supply Chain Hardening

**Last updated:** 2026-05-12

**Author:** Joshua Levy (github.com/jlevy) and LLM assistance

Operational hardening recipes and threat-model research for the four major open-source package ecosystems: npm, PyPI, crates.io, and Go modules. Through May 2026, the supply-chain attack wave on these ecosystems has accelerated from roughly monthly to weekly named incidents, compromising packages with billions of combined weekly downloads.

## Why This Repo Exists

Most attacks in the 2025-2026 wave share a pattern: malicious package versions live for minutes to hours before researchers detect them and the upstream maintainer or registry yanks the bad release. A 7-day rolling install quarantine plus disabled install-time scripts defeats the overwhelming majority of them. The per-ecosystem guides translate that pattern into copy-pasteable commands.

## Layout

Two documents per ecosystem:

- **Hardening guidelines** (`hardening-<ecosystem>.md`): minimum hardening steps, compromise-assessment commands, and CI enforcement snippets. Brief by design.
- **Research doc** (`research-<ecosystem>-supply-chain-hardening.md`): full threat model, attack timeline, per-platform and per-shell setup, IOC feeds, and scanning-tool comparisons.

The hardening guidelines doc is the action list. The research doc is the backup reference. Both doc categories share a common update procedure documented in [`self-update-instructions.md`](self-update-instructions.md).

## Ecosystems

| Ecosystem | Hardening Guidelines | Research Doc | Status |
| --- | --- | --- | --- |
| npm (Node.js) | [hardening-npm.md](hardening-npm.md) | [research-npm-supply-chain-hardening.md](research-npm-supply-chain-hardening.md) | Complete |
| PyPI (Python) | _pending_ | _pending_ | Planned; will follow the npm template |
| crates.io (Rust) | _pending_ | _pending_ | Planned; will follow the npm template |
| Go modules | _pending_ | _pending_ | Planned; will follow the npm template |

The npm pair is the structural template for the others. PyPI, crates.io, and Go guides will be added in subsequent iterations following the procedure in `self-update-instructions.md` → "Adding A New Ecosystem".

## Contributing

Each new ecosystem guide must:

1. Cite multiple independent sources for any named-incident claim.
2. Be specific enough to copy-paste: exact env-var names, exact filenames, exact version numbers.
3. Cover macOS, Linux, and Windows where the underlying tooling supports them.
4. End with the standard doc-guidelines footer.
5. Follow the procedure in [`self-update-instructions.md`](self-update-instructions.md).

## License

[MIT](LICENSE).

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
