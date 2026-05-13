---
type: is
id: is-01krerf4xphzt5wxrcsben07m0
title: Verify PyPI recommendations against current expert consensus
kind: task
status: closed
priority: 1
version: 5
labels:
  - validation
  - pypi
dependencies: []
created_at: 2026-05-12T18:51:24.982Z
updated_at: 2026-05-12T20:56:37.066Z
closed_at: 2026-05-12T20:56:37.065Z
close_reason: "Doc recommendations align with current expert consensus. (1) PyPA: pip-audit, --require-hashes, Trusted Publishing with Sigstore attestations all recommended (pip.pypa.io/en/stable/topics/secure-installs). (2) Astral/uv: --exclude-newer with friendly durations, --only-binary :all:, uv.lock with hashes by default (docs.astral.sh/uv/reference/settings). (3) Snyk: recommends provenance verification, behavioral analysis layer, cooldowns (snyk.io/blog/tanstack-npm-packages-compromised). (4) Socket: per-package risk scoring, behavioral analysis for install scripts (socket.dev). (5) StepSecurity: first public detector for multiple PyPI incidents, recommends cooldowns (stepsecurity.io/blog). (6) Phylum: supply-chain-specific behavioral analysis. (7) Broader consensus (nesbitt.io, bernat.tech, pydevtools.com): 7-day cooldown, hash-pinned lockfiles, refuse sdists, prefer uv. Poetry 2.4.0 adding solver.min-release-age shows ecosystem convergence on cooldown pattern. No drift found between doc recommendations and current expert guidance."
---
Compare research-pypi recommendations against current PyPA, Astral (uv), Snyk, Socket, StepSecurity guidance. Identify drift.
