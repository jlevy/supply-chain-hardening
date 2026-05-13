---
type: is
id: is-01krfaben9ca381zwmq8ejcsge
title: Address senior engineering review of supply chain hardening guidebook
kind: epic
status: closed
priority: 1
version: 23
labels: []
dependencies: []
child_order_hints:
  - is-01krfaemnt8reqgqak35hnfpcr
  - is-01krfaemv32r3m2wdtbkz2k4ht
  - is-01krfaemzrcfyc07g6djejghyg
  - is-01krfaen4bge0w4d99bb50mfag
  - is-01krfafyses9nwj5vv4ycc8f2j
  - is-01krfafyy66yvkct59gaxx6e6s
  - is-01krfafz2rnkf83bz2z9pharb3
  - is-01krfahsyw84qanr6wp94b9nf2
  - is-01krfaht36k450vtkxyd6jgtbq
  - is-01krfaht7djywhy0m0rvexg9f2
  - is-01krfahtbmp0ter5fgfvyvng15
  - is-01krfahtfsx6pqz8qa4n9cdpk9
  - is-01krfak4px636erwt5dz79c01d
  - is-01krfak4v29wc9b3rgzzysexzs
  - is-01krfak4z9c33hyvqkgjg77vw2
  - is-01krfamnn62bzc1tv8amwjx2vy
  - is-01krfamntd3hqvcdk8058xcj9q
  - is-01krfamnywbk25vg5gsv70j625
  - is-01krfamp3a8kckmzq8687fcfy2
  - is-01krfamp7yt4dk01fa7wf9w24y
created_at: 2026-05-13T00:03:58.248Z
updated_at: 2026-05-13T01:41:42.746Z
closed_at: 2026-05-13T01:41:42.744Z
close_reason: "All 20 sub-beads closed. Repository now: (HIGH) UV_ONLY_BINARY replaced with UV_NO_BUILD, pip precedence corrected, pnpm config-source semantics split into npm/pnpm subsections, pending-citation watch-list rows moved to Unverified section. (MEDIUM-HIGH) npm/pnpm naming cheat-sheet added; Go Step 0 toolchain CVE; cool-off framing tightened across README and portable doc; audit_npm.py reviewed (added backoff, MAL exit code 3). (MEDIUM) Strict-mode doc, SECURITY_MODEL.md, untrusted-repo-first-run.md, AGENTS.md agent rules with audit-log redaction; verify commands improved; CI examples pinned with test commands; ecosystem fine-grained corrections (npm ci, pnpm strictDepBuilds, dep confusion, proc-macros, GOPRIVATE/replace policy); language hyperbole bounded. (LOW) Incident response normalised to 8 steps across all four playbooks; doc-lint CI with known-env-vars allow-list catches the UV_ONLY_BINARY-class bug; MAINTENANCE.md last-verified table; watch list split into actionable vs contextual."
---
# Senior Engineering Review Remediation (2026-05-12)

Source: supply-chain-hardening-engineering-review.md (GPT-5.5 Pro review) plus
agent-side senior review and verification against current upstream docs.

## Reviewer's bottom line

The repo is close to a strong public security resource. The conceptual model is right,
the organization is good, and the operational guidance is unusually actionable. Before
broad distribution, fix the package-manager correctness issues and tighten the claims
around release-age gating.

## Triage approach

Sub-beads are grouped by severity. HIGH-severity beads are blockers for treating this
repo as production guidance; they fix functionally-incorrect controls users may believe
are active. MEDIUM-HIGH beads are semantic-precision fixes that affect trust. MEDIUM
beads add controls and clarity. ARCHITECTURE beads expand scope to team-level posture
and should be evaluated against the repo's stated mission ("methodology resource for
agents and humans," not a full enterprise security program).

## Verification done before triage

I verified the three most-load-bearing reviewer claims against current upstream docs
before opening these beads:

- UV_ONLY_BINARY is not a documented uv env var. Confirmed against
  docs.astral.sh/uv/reference/environment/. UV_NO_BUILD is the correct equivalent of
  --no-build (refuse sdists). --only-binary is exposed as a command-line flag and as
  only-binary in [tool.uv.pip] project config, not as an env var.
- pnpm .npmrc is auth/registry only in current pnpm. Confirmed against
  pnpm.io/settings. Non-auth pnpm settings come from CLI, env vars, and
  pnpm-workspace.yaml / ~/.config/pnpm/config.yaml.
- pip does not read pyproject.toml [tool.pip] as a config source. Confirmed against
  pip.pypa.io/en/stable/topics/configuration/. The pip precedence chain documented in
  research-pypi-supply-chain-hardening.md (project-local [tool.pip] / setup.cfg) is
  wrong.

## Agent-side judgments distinct from reviewer

Areas where I am applying senior judgment rather than blindly following the review:

1. Scope. The "Better Architecture" layered model the reviewer proposes (dev defaults
   to project policy to CI to org registry/proxy to sandbox to IR) is sound, but
   Layer 4 (org registry/proxy controls) is explicitly out of scope in the PyPI
   research doc and would substantially expand the repo's mission. We will add a
   short SECURITY_MODEL.md that names the layers and references each, but we will
   not write end-to-end Artifactory/Nexus/Verdaccio setup guides in this round.
2. "Pending direct citation" rows in compromised-packages.md. Reviewer is correct
   that these should not appear in the canonical table. We will move them to a
   separate "Unverified / pending verification" section rather than delete, so
   attribution work is preserved.
3. "Defeats nearly all of it" language. Reviewer flags hyperbole. We agree and will
   bound the claim to the named fast-yanked incidents.
4. scripts/audit_npm.py code review. Reviewer explicitly could not review this. We
   will book a separate bead for a real code review of the script (OSV API handling,
   scoped-package parsing, rate limiting, exit codes) because that script is
   load-bearing for the npm hardening flow.

## Out of scope for this epic

- Building actual registry mirrors/proxies (Artifactory/Nexus/Verdaccio/devpi).
- A full strict-mode reference implementation as runnable scripts. We will add a
  strict-mode/balanced-mode/emergency-exception doc matrix but not a separate
  strict-mode CLI.
- Container/sandbox tooling beyond linking to existing options.

See sub-beads for the per-issue triage and recommended approach.
