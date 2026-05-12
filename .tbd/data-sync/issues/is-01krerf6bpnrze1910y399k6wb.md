---
type: is
id: is-01krerf6bpnrze1910y399k6wb
title: Verify Go tool coverage and CI snippets
kind: task
status: closed
priority: 1
version: 2
labels:
  - validation
  - go
dependencies: []
created_at: 2026-05-12T18:51:26.453Z
updated_at: 2026-05-12T20:02:42.989Z
closed_at: 2026-05-12T20:02:42.988Z
close_reason: govulncheck install via 'go install golang.org/x/vuln/cmd/govulncheck@latest' is current canonical command per go.dev. osv-scanner -L go.mod supported. go mod verify + go mod tidy -diff both standard. CI snippets follow standard go patterns.
---
Verify govulncheck (call-graph awareness), osv-scanner -L go.mod, go mod verify, go mod tidy -diff. Test CI snippets against current Go versions.
