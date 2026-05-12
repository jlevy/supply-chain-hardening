---
type: is
id: is-01krerf3ena85h8462kmz0eybj
title: Verify TanStack Mechanism And Indicators section
kind: task
status: closed
priority: 1
version: 3
labels:
  - validation
  - npm
dependencies: []
created_at: 2026-05-12T18:51:23.476Z
updated_at: 2026-05-12T18:59:06.173Z
closed_at: 2026-05-12T18:59:06.166Z
close_reason: Verified all TanStack IOCs in research-npm doc. router_init.js SHA-256 ab4fcadaec49... confirmed (StepSecurity). getsession.org domains (filev2, seed1-3) confirmed (TanStack postmortem, Aikido, SafeDep). TLS cert CN=seed1.getsession.org, O=Oxen Privacy Tech Foundation confirmed (StepSecurity). GHSA-g7cv-rxg3-hmpx confirmed (github.com/advisories). CVE-2026-45321 confirmed (NVD). CVSS 9.6 confirmed. Patched @tanstack/react-router@1.169.9, malicious 1.169.5-1.169.8 confirmed (GHSA). Persistence locations (.claude/settings.json, .vscode/tasks.json, systemd/LaunchAgent) confirmed (StepSecurity); StepSecurity lists additional paths (.claude/router_runtime.js, .claude/setup.mjs, ~/Library/LaunchAgents/com.user.gh-token-monitor.plist, ~/.config/systemd/user/gh-token-monitor.service) not in doc but existing claims correct. No issues requiring correction.
---
Verify every IOC in research-npm-supply-chain-hardening.md TanStack section: router_init.js SHA-256, getsession.org domains, TLS cert pin, persistence locations (.claude/, .vscode/, systemd), GHSA-g7cv-rxg3-hmpx, CVE-2026-45321, CVSS 9.6, patched version. Cross-check with TanStack postmortem + StepSecurity.
