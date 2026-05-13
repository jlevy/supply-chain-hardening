---
type: is
id: is-01krfahtbmp0ter5fgfvyvng15
title: Address ecosystem-specific fine-grained corrections (npm ci, pnpm strictDepBuilds, dep confusion, proc-macros, GOPRIVATE)
kind: task
status: open
priority: 2
version: 1
labels:
  - docs
dependencies: []
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:07:26.835Z
updated_at: 2026-05-13T00:07:26.835Z
---
# Add ecosystem-specific operational gaps the reviewer flagged

## Problem

The reviewer's "Fine-Grained Corrections" list contains a number of
ecosystem-specific additions that are clearly correct but small. Grouping
them into one bead avoids bead proliferation; each one is a 1-3 line edit.

## Fix (per ecosystem)

**npm / pnpm**

- Document `npm ci` as the required non-mutating install mode for npm
  users (currently the doc emphasizes pnpm's `frozen-lockfile` but does
  not explicitly say npm users must use `npm ci`).
- Add the strict-mode agent rule "no `npx`, no `pnpm dlx`, no `bunx`"
  (lives in the new strict-mode doc; cross-link from hardening-npm.md).
- Document pnpm's `strictDepBuilds` / `allowBuilds` (current pnpm version
  terminology). If terminology has changed since the doc was last
  validated, verify against pnpm.io/settings before editing.

**PyPI / uv / pip**

- Add a dependency-confusion subsection to guidelines/hardening-pypi.md:
  avoid `--extra-index-url` for private packages; use isolated indexes
  with explicit per-package routing.
- Caveat that `PIP_UPLOADED_PRIOR_TO` depends on index-provided upload
  metadata (private indexes may not expose this).
- Caveat the syntactic difference between `UV_EXCLUDE_NEWER="7 days"`
  and `PIP_UPLOADED_PRIOR_TO="P7D"`; they are not interchangeable.

**crates.io**

- Clarify that `cargo vet certify` should only be used after actual
  review. For temporary unvetted needs, use a documented exemption, not
  certification.
- Add proc-macro review alongside `build.rs` review in the short
  playbook (currently only research doc emphasizes proc-macros).
- Improve `cargo deny` examples with version-specific bans where
  possible.
- Note that aliases (e.g. `alias cargo='cargo --locked'`) protect only
  interactive use; scripts, CI, and tools that call `cargo` directly
  bypass aliases.

**Go**

- Add a source-policy check for unexpected `replace`/`exclude` directives
  in go.mod, and for overly-broad `GOPRIVATE`/`GONOSUMDB`.
- Clarify that `GOFLAGS=""` bypass removes ALL Go default flags, not
  only `-mod=readonly`.
- Add a check for `go.work` files.

## Files to edit

- guidelines/hardening-npm.md
- guidelines/hardening-pypi.md
- guidelines/hardening-crates.md
- guidelines/hardening-go.md
- research/* where reflections of these are needed (usually a one-line
  link back to the playbook)

## Acceptance

- Each fine-grained correction is addressed in the operational playbook,
  not just buried in the research doc.
- pnpm-specific terminology has been re-validated against pnpm.io/settings.
- Operational playbooks reference proc-macro review for Rust and source
  policy for Go.
