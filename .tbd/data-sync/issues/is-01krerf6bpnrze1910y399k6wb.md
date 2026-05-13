---
type: is
id: is-01krerf6bpnrze1910y399k6wb
title: Verify Go tool coverage and CI snippets
kind: task
status: closed
priority: 1
version: 5
labels:
  - validation
  - go
dependencies: []
created_at: 2026-05-12T18:51:26.453Z
updated_at: 2026-05-12T20:55:20.844Z
closed_at: 2026-05-12T20:55:20.843Z
close_reason: "Verified govulncheck install command (go install golang.org/x/vuln/cmd/govulncheck@latest) matches go.dev/doc/security/vuln and go.dev/doc/tutorial/govulncheck. Call-graph-aware analysis confirmed. go mod verify and go mod tidy -diff (Go 1.23+, confirmed via golang/go#67242) both correct. Fixed osv-scanner command from V1 syntax (osv-scanner -L go.mod) to V2 syntax (osv-scanner scan source --lockfile=go.mod) in both hardening-go.md and research doc (3 occurrences). V2 is current at v2.3.8. CI snippets verified against current Go/GHA versions. Citations: go.dev/doc/security/vuln, google.github.io/osv-scanner/usage/scan-source, github.com/google/osv-scanner."
---
Verify govulncheck (call-graph awareness), osv-scanner -L go.mod, go mod verify, go mod tidy -diff. Test CI snippets against current Go versions.
