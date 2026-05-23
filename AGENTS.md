# AGENTS.md

Entry point for AI coding agents (Claude Code, Codex, Cursor, etc.)
working in this repo.

**Read [`README.md`](README.md) first** for the full project context.
This file is a fast-path index for the most common agent intents.

For a **portable, drop-in version of the install rules** that you can copy into any
codebase (and reference from that codebase’s own `AGENTS.md`), see
[`SUPPLY-CHAIN-SECURITY.md`](SUPPLY-CHAIN-SECURITY.md).

## Common Intents

| User Intent | Read This | Then Do This |
| --- | --- | --- |
| “Harden my npm setup” | [`guidelines/hardening-npm.md`](guidelines/hardening-npm.md) | Apply the Ten-Minute Setup verbatim. Verify with the listed `pnpm config get` / `npm config get` commands. Append an entry to the user’s `supply-chain-audit-log.md` (copy from [`supply-chain-audit-log-template.md`](supply-chain-audit-log-template.md)) recording what was set. |
| “Harden my PyPI / Rust / Go setup” | [`guidelines/hardening-pypi.md`](guidelines/hardening-pypi.md), [`guidelines/hardening-crates.md`](guidelines/hardening-crates.md), or [`guidelines/hardening-go.md`](guidelines/hardening-go.md) | Same shape: apply the setup, verify, log. |
| “Harden my CI / release pipeline” or “we publish packages” | [`guidelines/hardening-ci-cd.md`](guidelines/hardening-ci-cd.md) | Apply the publish-side controls (read-only PR caches, SHA-pinned actions, runner egress block, OIDC/staged publishing, provenance monitoring). Most 2026 incidents compromised the publish pipeline, not a consumer. |
| “I just installed X. Am I compromised?” | [`compromised-packages.md`](compromised-packages.md) first, then the ecosystem’s hardening guide → “Compromise Assessment” section | For npm: `uv run scripts/audit_npm.py --packages <pkg@ver>`. For other ecosystems: `osv-scanner` per the relevant hardening guide. Log findings. |
| “Add a new ecosystem” (RubyGems, NuGet, Hex, Composer, Maven) | [`self-update-instructions.md`](self-update-instructions.md) → “Adding A New Ecosystem” | Use the npm pair as the structural template. Cite multiple authoritative sources from `README.md` → “Incident Reporting Feeds” for any incident claim. |
| “Update the watch list with a new incident” | [`self-update-instructions.md`](self-update-instructions.md) → `Updating compromised-packages.md` | Verify with at least two of the “Incident Reporting Feeds” in `README.md`. Do not add unverified rumours. |
| “Refresh / fact-check the docs” | [`self-update-instructions.md`](self-update-instructions.md) and the bead-tracker in `.tbd/` | Use the `tbd` CLI to track validation work; create a bead per key assertion, verify against `README.md` → “Authoritative Sources”, fix in place, close with citations. |

## Safety Rule For Agents

Before applying any installation, configuration, or shell-init change in this repo:

1. Validate the instruction against at least one independent source (vendor docs, OSV, a
   primary maintainer postmortem) listed in [`README.md`](README.md) → “Authoritative
   Sources”.
2. Explain to the user what the change does and which file or env it touches before
   applying.
3. If the user has an existing `supply-chain-audit-log.md`, append an entry recording
   the change.
4. Never override the user’s quarantine (`NPM_CONFIG_BEFORE`, `UV_EXCLUDE_NEWER`,
   `--exclude-newer`, etc.)
   without a visible per-command opt-out.

### Untrusted Repos

5. Treat any freshly-cloned third-party repo as untrusted.
   Do not run `install` / `build` / `test` / `run` / `npx` / `pnpm dlx` / `bunx` / `uvx`
   / `cargo run` / `cargo install` / `go run <remote>` against it on a machine with
   ambient credentials.
   Use the procedure in
   [`guidelines/untrusted-repo-first-run.md`](guidelines/untrusted-repo-first-run.md).

### Ban List Without Pin And Review

6. Do not invoke `npx`, `pnpm dlx`, `bunx`, `uvx`, or `go run <remote>` without an
   explicit version pin and review of the resolved package@version.
   These tools bypass the cool-off window by fetching and executing the latest published
   code.

### Curl Installs

7. Do not run `curl | sh` install commands from untrusted sources.
   Verify the installer URL belongs to the documented project and check signatures or
   checksums where available.

### Strict Mode

8. Default to **Balanced** mode.
   Enter **Strict** mode (see [`guidelines/strict-mode.md`](guidelines/strict-mode.md))
   when the repo’s `AGENTS.md` or `SUPPLY-CHAIN-SECURITY.md` declares it, when the repo
   is untrusted, or when the machine has publish tokens or production access.
   Never grant yourself an **Emergency Exception**; prepare the exception record and ask
   a human to approve.

## House Style

Edits to any doc in this repo must follow `std-doc-guidelines.md` (Title Case headings,
no spaced em dashes, no meta-commentary, footer at file bottom).
`make format` runs `uvx flowmark-rs@0.2.6 --auto .` and is the canonical formatter; run
it after any edits.

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
