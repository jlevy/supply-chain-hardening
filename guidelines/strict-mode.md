# Strict, Balanced, And Emergency-Exception Modes

**Last updated:** 2026-05-23

**Author:** Joshua Levy (github.com/jlevy) with agent assistance

The per-ecosystem playbooks are written for the Balanced default.
This doc names two other postures (Strict and Emergency Exception) and documents how to
switch between them.

## Modes At A Glance

| Control | Balanced (default) | Strict | Emergency Exception |
| --- | --- | --- | --- |
| Release-age cool-off | 14 days where the package manager supports it | 14-day minimum; no upgrade without reviewing the dependency’s change set (do not update for its own sake); weekly review of bypass logs | per-command bypass with reason logged |
| Install / lifecycle scripts | disabled (`NPM_CONFIG_IGNORE_SCRIPTS=true`) | disabled; allowlist required for any exception | disabled; exceptions require approval |
| Source builds (PyPI sdists, `build.rs`, proc-macros) | refused (`UV_NO_BUILD=true`, `PIP_ONLY_BINARY=:all:`) | refused, with sandbox for unavoidable cases | sandbox + approver |
| Lockfile | committed; `--frozen` / `--locked` / `npm ci` | committed; `cargo vet` or equivalent attestation required | unchanged |
| Untrusted-repo first run | recommended sandbox | mandatory sandbox (see [untrusted-repo-first-run.md](untrusted-repo-first-run.md)) | mandatory sandbox |
| Network-from-build | allowed during install / build | egress allowlist only | egress allowlist + approver |
| `npx` / `pnpm dlx` / `bunx` / `uvx` / `go run <remote>` | discouraged; allowed with pin + review | banned | per-command exception |
| `GOTOOLCHAIN` | unset (allow proxy-fetched toolchains under fixed Go) | `local` (no automatic toolchain downloads) | unset |
| CI scanner versions | pinned where convenient | pinned; checksum-verified install | pinned |

## When To Use Each Mode

- **Balanced** for normal product work, small teams, and personal developer
  workstations. Catches the dominant fast-yanked-incident pattern.
- **Strict** for security-sensitive codebases, AI agents that run arbitrary
  user-provided repos, CI runners for high-value secrets, and machines that hold publish
  tokens or production credentials.
- **Emergency Exception** for a single install when an upstream just shipped a critical
  patch inside the cool-off window.
  Log it (see template below) and revert to the baseline mode for the next command.

## Switching On Strict Mode

Apply the per-ecosystem additions on top of the Balanced shell-init:

- npm / pnpm: set `NPM_CONFIG_BEFORE` to `now-14d` (or `MIN_RELEASE_AGE=14`,
  `MINIMUM_RELEASE_AGE=20160`). Ban `npx` and `pnpm dlx` in agent rules.
  Require `pnpm-workspace.yaml` build-script allowlist (`onlyBuiltDependencies` /
  `strictDepBuilds` per current pnpm).
- PyPI / uv / pip: set `UV_EXCLUDE_NEWER="14 days"`, `PIP_UPLOADED_PRIOR_TO="P14D"`.
  Keep `UV_NO_BUILD=true` and `PIP_ONLY_BINARY=:all:`. Require hash-pinned requirements
  for pip (`--require-hashes`). Refuse `--extra-index-url`; use isolated indexes for
  private packages.
- Cargo: keep `--locked` everywhere; require `cargo vet` certifications for every new
  crate; ban `cargo run` for code paths not under review.
  Run all builds and tests in the [untrusted-repo sandbox](untrusted-repo-first-run.md)
  when adding a dependency for the first time.
- Go: set `GOTOOLCHAIN=local`. Forbid `replace` directives in `go.mod` except via a
  reviewed PR. Run `go test ./...` only inside the sandbox for untrusted code.

## Emergency Exception Record

When a strict or balanced setup must accept a fresh install (CVE patch, urgent fix from
an upstream you trust):

```text
Package: <name>
Version: <pinned exact version, not a range>
Reason: <why this exception is necessary; cite advisory ID if applicable>
Source verification:
  - <what was checked: GHSA / OSV record, maintainer attestation, Sigstore / PyPI
     Trusted Publisher signature, blog or release-notes URL>
Approver: <human; not the agent>
Rollback plan:
  - <how to revert if it turns out to be malicious; usually: pin to
     <previous-known-good>, regenerate lockfile, run scanner>
Logged in: <supply-chain-audit-log.md entry under YYYY-MM-DD>
```

Paste this into the commit message or PR description for the exception.
Append a matching entry to your `supply-chain-audit-log.md` (see
[`supply-chain-audit-log-template.md`](../supply-chain-audit-log-template.md)) with
`### Actions Taken` and a `### Pending Actions` follow-up to confirm the package was not
yanked after the fact.

## Agent Defaults

- Agents default to **Balanced**.
- An agent enters **Strict** when:
  - The project’s `AGENTS.md` or `SUPPLY-CHAIN-SECURITY.md` declares it explicitly.
  - The repo is untrusted (see
    [untrusted-repo-first-run.md](untrusted-repo-first-run.md)).
  - The agent is operating on a machine with publish tokens or production access.
- An agent never grants itself an **Emergency Exception**. It can prepare the exception
  record (above) for human approval, but it must not execute the install until a human
  signs off.

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
