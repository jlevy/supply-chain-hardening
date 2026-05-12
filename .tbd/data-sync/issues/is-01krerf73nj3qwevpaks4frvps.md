---
type: is
id: is-01krerf73nj3qwevpaks4frvps
title: Verify scripts/audit-npm.py against current OSV API spec
kind: task
status: closed
priority: 2
version: 3
labels:
  - validation
  - cross-cutting
dependencies: []
created_at: 2026-05-12T18:51:27.220Z
updated_at: 2026-05-12T18:55:13.884Z
closed_at: 2026-05-12T18:55:13.883Z
close_reason: "Verified scripts/audit-npm.py against current OSV API spec. Request shape ({package: {name, ecosystem}, version}) matches POST /v1/query and /v1/querybatch docs at google.github.io/osv.dev. Response shape ({results: [{vulns: [{id, modified}]}]}) matches. 'affected[].versions' field used by advisory_affects_version() is documented. 'npm' is the documented ecosystem identifier. MAL-* prefix for malicious-package advisories follows OSV-Schema convention (verified empirically via qix test cases). Fixed inaccurate comment claiming OSV documents a batch-size max of 1000 — OSV does not formally document the limit; 1000 is a conservative choice that works in practice. No auth required (script does not send any); 32MiB response limit is well above realistic audit-tree sizes."
---
Verify scripts/audit-npm.py uses current OSV API endpoints (/v1/querybatch, /v1/vulns/ID), correct batch size (1000), correct request/response shape. Test the advisory_affects_version() versions-list filter against real OSV advisories. Confirm MAL- prefix is still the canonical malicious-package indicator.
