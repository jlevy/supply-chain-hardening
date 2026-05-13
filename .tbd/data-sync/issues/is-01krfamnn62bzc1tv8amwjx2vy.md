---
type: is
id: is-01krfamnn62bzc1tv8amwjx2vy
title: Code-review scripts/audit_npm.py (OSV API, scoped parsing, rate limit, exit codes)
kind: task
status: closed
priority: 1
version: 3
labels:
  - correctness
  - npm
  - audit-script
dependencies: []
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:09:00.321Z
updated_at: 2026-05-13T01:31:39.452Z
closed_at: 2026-05-13T01:31:39.446Z
close_reason: "Reviewed scripts/audit_npm.py. Added: (1) bounded exponential backoff on OSV HTTP requests (4 attempts, 1s/2s/4s delays, retries 408/429/5xx and URLError). (2) Distinct exit code 3 for MALICIOUS-tagged advisories, keeping 1 for ordinary CVE. Verified all four exit codes work: lodash@4.17.21 -> 1, chalk@5.6.1 -> 3 (MAL-2025-46969), express@4.21.0 -> 0, bad spec -> 2. Updated scripts/README.md and CLI epilog to document the new exit-code semantics. Original strengths kept as-is: scoped-package parsing via rfind('@'), MAL-* only tagging (not summary heuristic), explicit affected.versions filter to avoid over-broad SEMVER matches, stdlib-only with PEP 723 deps=[]."
---
# Code-review scripts/audit_npm.py

## Problem

Reviewer explicitly could not review this script. It is load-bearing for
the npm hardening flow (the README's "Harden All Ecosystems" Step 4
recommends it; hardening-npm.md uses it for global-tree audits).

## Scope

Read scripts/audit_npm.py end-to-end and verify:

1. **OSV API handling.** Correct request shape for /v1/query and
   /v1/querybatch; correct batching (limit 1000 per batch); retry/backoff
   on 429 and 5xx; explicit timeouts.
2. **Scoped-package parsing.** `@scope/name@version` strings are split
   correctly (the @ in scope must not be confused with the version
   separator).
3. **Lockfile / global tree walking.** Walking `node_modules` from the
   correct root; handling of pnpm's flat store; handling of npm 7+'s
   nested layout.
4. **Rate limiting.** Either honors OSV's published rate limits or has
   client-side throttling. No request loops on transient errors.
5. **Error handling.** Network failure does not silently exit 0; user
   sees a clear error.
6. **Exit codes.** Documented in the script and in scripts/README.md;
   distinguish "MALICIOUS found" from "ordinary CVE found" from "no
   findings" from "scanner error".
7. **Output format.** Stable enough that a CI job can grep on it.
8. **Dependencies.** Stdlib-only (claim in hardening-npm.md). Confirm.
9. **Maliciousness markers.** OSV uses MAL-* IDs and database = "MAL";
   verify the script recognises both.

## Fix

For each issue found, either:

- Fix in scripts/audit_npm.py with a short PR-friendly commit.
- Document the limitation in scripts/README.md if it is intentional.

Add a self-test or example invocation in scripts/README.md that exercises
both the directory-scan and the `--packages` mode.

## Files to edit

- scripts/audit_npm.py
- scripts/README.md (if usage / exit codes need clarification)

## Acceptance

- Script handles 429/5xx with backoff and explicit timeout.
- Scoped-package parsing has at least one targeted test case (in a
  comment or a docstring example).
- Exit codes distinguish at least MALICIOUS / CVE / clean / error.
- README documents what is checked and what is out of scope.
