---
type: is
id: is-01krerf49cx7tyanzqqn2c3gka
title: Verify all PyPI incident rows in compromised-packages.md
kind: task
status: closed
priority: 1
version: 3
labels:
  - validation
  - pypi
dependencies: []
created_at: 2026-05-12T18:51:24.331Z
updated_at: 2026-05-12T18:57:20.165Z
closed_at: 2026-05-12T18:57:20.160Z
close_reason: "Verified all 5 PyPI incident rows. ctx: date 2022-05-14, expired-domain takeover, env-var exfil confirmed. torchtriton: Dec 25-30 2022, v2.0.0, ~2700 downloads, DNS exfil to *.h4ck.cfd confirmed via PyTorch blog. Ultralytics: Dec 4 2024, versions 8.3.41/42/45/46, pull_request_target + @openimbot + XMRig confirmed via Snyk. LiteLLM: Mar 24 2026, v1.82.7/8, TeamPCP, Trivy CI compromise, GHSA-5mg7-485q-xm76, 95M monthly confirmed. TanStack cross-ecosystem: May 11 2026, mistralai@2.4.6 + guardrails-ai@0.10.1 confirmed via SafeDep/Wiz/THN. No discrepancies found."
---
For each PyPI row: ctx (2022-05-14), torchtriton (2022-12-25), Ultralytics (2024-12-04), LiteLLM (2026-03-24), TanStack cross-ecosystem mistralai@2.4.6+guardrails-ai@0.10.1 (2026-05-11): verify dates, versions, scale, vector, references resolve.
