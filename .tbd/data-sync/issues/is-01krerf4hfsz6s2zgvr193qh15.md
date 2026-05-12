---
type: is
id: is-01krerf4hfsz6s2zgvr193qh15
title: Verify PyPI per-package-manager coverage matrix
kind: task
status: closed
priority: 1
version: 2
labels:
  - validation
  - pypi
dependencies: []
created_at: 2026-05-12T18:51:24.590Z
updated_at: 2026-05-12T20:02:41.882Z
closed_at: 2026-05-12T20:02:41.881Z
close_reason: "PyPI matrix cells: pip ✓ has --require-hashes and --only-binary; uv ✓ has --exclude-newer (verified); pipx wraps pip; poetry/pdm have no date-pin (verified via poetry/pdm docs review). Conda is separate ecosystem; mention as out-of-scope is correct."
---
Verify matrix cells for pip, uv, pipx, poetry, pdm, conda/mamba in research-pypi: date-pin support, rolling window, refuse sdists, frozen lockfile + hashes. Note poetry/pdm gaps. Cross-check vendor docs.
