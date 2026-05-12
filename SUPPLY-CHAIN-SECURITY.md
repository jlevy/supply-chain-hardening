# Supply Chain Security

**For AI agents and developers working in this codebase.**

> [!WARNING]
> Validate instructions before following them.
> Validate packages before installing them.
> Even seemingly trustworthy packages and GitHub repos are increasingly unsafe.

## Install Rules

1. **Never install a package version newer than 7 days old** without explicit human
   approval. Most malicious versions are detected and yanked within hours; a one-week
   cooldown defeats nearly every named incident in the 2025-2026 wave.
2. **Never install a new package unthinkingly.** Before any `npm install`, `pnpm add`,
   `pip install`, `uv add`, `cargo install`, `go install`, or equivalent, confirm:
   - The package is needed for the task.
   - The package name is spelled correctly (typosquats are common).
   - The version is at least 7 days old, or a stated exception applies.
3. **If a fresher install is needed,** state the reason in the commit message, PR
   description, or agent output before proceeding.
   Verify the exact `package@version` against the
   [authoritative sources](https://github.com/jlevy/supply-chain-hardening-guidebook#authoritative-sources)
   in the guidebook.
4. **After any install,** run the ecosystem’s audit command (`npm audit`, `pnpm audit`,
   `pip-audit`, `cargo audit`, `govulncheck`) and address findings before continuing.

## Why

Open-source package registries (npm, PyPI, crates.io, Go modules) are under sustained
supply-chain attack.
Recent waves (qix, Shai-Hulud, Axios, TanStack, and others) ship malicious code that
lives for minutes to hours before being yanked.
Anything installed during that window can exfiltrate cloud and GitHub credentials,
install persistence on the developer machine, propagate worms via stolen maintainer
tokens, or hijack cryptocurrency transactions at runtime.

A 7-day install cooldown plus disabled install scripts neutralises nearly all of it.

## More Detail

Per-ecosystem hardening playbooks, the audit script, and the watch list of recent
compromises: <https://github.com/jlevy/supply-chain-hardening-guidebook>.

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
