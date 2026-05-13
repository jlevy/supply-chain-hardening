---
type: is
id: is-01krerf4sfp9sgsa6rf3e1navv
title: Verify PyPI IOC feeds and scanning tools
kind: task
status: closed
priority: 1
version: 5
labels:
  - validation
  - pypi
dependencies: []
created_at: 2026-05-12T18:51:24.846Z
updated_at: 2026-05-12T20:56:25.996Z
closed_at: 2026-05-12T20:56:25.995Z
close_reason: "Verified and updated scanning tools. (1) pip-audit: PyPA/Trail of Bits, backed by PyPA Advisory DB + optional OSV. Install via 'pip install pip-audit' or 'uv tool install pip-audit'. Current version 2.9.0. Confirmed at pypi.org/project/pip-audit and github.com/pypa/pip-audit. (2) safety: Safety/PyUp, v3.7.0. UPDATED doc: 'safety scan' is now the recommended command in Safety 3.x (recursive discovery). 'safety check -r requirements.txt' still supported for backward compatibility. Migration docs at docs.safetycli.com. (3) osv-scanner: Google, Go binary. UPDATED to V2 syntax: 'osv-scanner scan source -L requirements.txt'. V2 added transitive scanning for requirements.txt via deps.dev API. Current v2.3.5. Confirmed at google.github.io/osv-scanner/usage/scan-source. IOC feeds (OSV.dev, GHSA, PyPA Advisory DB, deps.dev): all URLs confirmed live."
---
Verify URLs and capabilities for: pip-audit (PyPA), safety, osv-scanner -L requirements.txt, OSV.dev PyPI feed, PyPA Advisory DB, GHSA PyPI. Verify each tool works as described against current docs.
