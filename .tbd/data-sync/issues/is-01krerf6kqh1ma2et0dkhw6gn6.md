---
type: is
id: is-01krerf6kqh1ma2et0dkhw6gn6
title: Verify Go IOC feeds and recommendations
kind: task
status: closed
priority: 1
version: 5
labels:
  - validation
  - go
dependencies: []
created_at: 2026-05-12T18:51:26.710Z
updated_at: 2026-05-12T20:55:34.738Z
closed_at: 2026-05-12T20:55:34.737Z
close_reason: "Verified all IOC feed URLs live. vuln.go.dev serves machine-readable JSON API (endpoints: /index/db.json, /index/modules.json, /index/vulns.json, /ID/$id.json) in OSV schema. pkg.go.dev/vuln/ is the browser UI (confirmed showing GO-2026-* entries). OSV.dev Go filter at osv.dev/list?ecosystem=Go confirmed live. GHSA Go filter at github.com/advisories?query=ecosystem:go shows 3788 reviewed advisories. Fixed deps.dev API URL from v3alpha to v3 (v3 is now stable per docs.deps.dev/api/v3). Tier 2 feeds (Socket.dev, Aikido Intel, StepSecurity, Datadog Security Labs) all verified as active. Citations: go.dev/doc/security/vuln/database, docs.deps.dev/api/v3, osv.dev, github.com/advisories."
---
Verify vuln.go.dev URL/format, pkg.go.dev/vuln UI, OSV.dev Go feed, GHSA Go filter. Compare recommendations against current Go security team guidance.
