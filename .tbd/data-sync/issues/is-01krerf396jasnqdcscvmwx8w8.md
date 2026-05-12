---
type: is
id: is-01krerf396jasnqdcscvmwx8w8
title: Verify all npm incident rows in compromised-packages.md
kind: task
status: closed
priority: 1
version: 3
labels:
  - validation
  - npm
dependencies: []
created_at: 2026-05-12T18:51:23.301Z
updated_at: 2026-05-12T18:58:28.512Z
closed_at: 2026-05-12T18:58:28.499Z
close_reason: "Verified all npm incident rows. Nx: date 2025-08 confirmed (The Register 2025-08-27); versions understated (Socket lists nx@20.9.0-21.8.0 + scoped packages at various versions, not just 21.5.x); proposed correction for shared file noted. qix: date 2025-09-08, 18+ packages, phishing via npmjs.help all confirmed (Socket, StepSecurity). Shai-Hulud 1.0: 2025-09-15 + @ctrl/tinycolor initial vector confirmed (Unit42, CISA, Sysdig). Shai-Hulud 2.0: 2025-11-24, 796 packages confirmed (Datadog, Wiz, Netskope). Aqua Trivy: March 2026 + TeamPCP confirmed; row describes it as 'Single scanner package' but primary vector was GitHub Actions, npm impact via CanisterWorm (47+ packages); proposed clarification for shared file noted. Axios: 2026-03-31, versions 1.14.1/0.30.4, Sapphire Sleet (DPRK) confirmed (CISA, Microsoft, Mandiant). Bitwarden CLI: April 2026, @bitwarden/cli@2026.4.0, TeamPCP confirmed (BleepingComputer, Socket). SAP @cap-js: 2026-04-29, mbt@1.2.48 + 3 @cap-js packages confirmed (THN, The Register, StepSecurity). Intercom+lightning: 2026-04-30, 4 versions confirmed (Socket, THN). TanStack: 2026-05-11, 84 versions/42 packages, GHSA-g7cv-rxg3-hmpx, CVE-2026-45321, CVSS 9.6 all confirmed (GHSA, TanStack postmortem, StepSecurity). All reference URLs resolve."
---
For each npm row in compromised-packages.md (Nx, qix, Shai-Hulud 1.0, Shai-Hulud 2.0, Aqua Trivy, Axios, Bitwarden CLI, SAP @cap-js, Intercom+lightning, TanStack): verify date, affected versions, scale numbers, vector description, and that all reference URLs resolve. Use OSV.dev, GHSA, maintainer postmortems.
