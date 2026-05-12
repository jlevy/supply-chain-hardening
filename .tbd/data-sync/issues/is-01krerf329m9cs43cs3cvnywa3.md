---
type: is
id: is-01krerf329m9cs43cs3cvnywa3
title: Verify npm Part 1 background claims
kind: task
status: closed
priority: 1
version: 3
labels:
  - validation
  - npm
dependencies: []
created_at: 2026-05-12T18:51:23.080Z
updated_at: 2026-05-12T18:57:38.440Z
closed_at: 2026-05-12T18:57:38.439Z
close_reason: "Verified Part 1 background claims: (1) account-takeover pattern confirmed via Socket/StepSecurity/Unit42 writeups for qix (phishing via npmjs.help), TanStack (pull_request_target + cache poisoning + OIDC theft), Shai-Hulud (token theft from prior victims). (2) Common lifetime minutes-to-hours confirmed across all named incidents. (3) 'standard practices not enough' reasoning verified against npm/pnpm docs (config precedence, audit lag, lockfile limitations). No issues found."
---
Fact-check Part 1 of research-npm-supply-chain-hardening.md: threat pattern (account takeover -> publish -> exfil/hijack), common lifetime (minutes-to-hours before yank), why standard practices fail. Cross-reference against current Aikido/StepSecurity/Socket/Unit42/Datadog writeups. Confirm claims still accurate as of search date.
