---
type: is
id: is-01krerf4hfsz6s2zgvr193qh15
title: Verify PyPI per-package-manager coverage matrix
kind: task
status: closed
priority: 1
version: 5
labels:
  - validation
  - pypi
dependencies: []
created_at: 2026-05-12T18:51:24.590Z
updated_at: 2026-05-12T20:56:05.323Z
closed_at: 2026-05-12T20:56:05.322Z
close_reason: "Verified matrix and updated doc. pip: --uploaded-prior-to (P7D), --only-binary :all:, --require-hashes all confirmed. uv: --exclude-newer, --only-binary :all:, uv sync --frozen with hashes all confirmed. pipx: correctly described as inheriting backend. UPDATED: Poetry now has solver.min-release-age (>=2.4.0, May 2026, PR #10824 merged); doc updated from 'no' to show this. pdm: --exclude-newer supports N{d|h|w} relative durations (v2.26.8+) plus pyproject.toml config (v2.26.9+); doc updated with format detail. conda: pre-built, no sdist risk, conda-lock for hashes; correct. Matrix table and strategic takeaway updated."
---
Verify matrix cells for pip, uv, pipx, poetry, pdm, conda/mamba in research-pypi: date-pin support, rolling window, refuse sdists, frozen lockfile + hashes. Note poetry/pdm gaps. Cross-check vendor docs.
