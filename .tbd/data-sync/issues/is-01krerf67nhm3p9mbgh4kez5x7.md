---
type: is
id: is-01krerf67nhm3p9mbgh4kez5x7
title: Verify Go hardening pattern
kind: task
status: closed
priority: 1
version: 7
labels:
  - validation
  - go
dependencies: []
created_at: 2026-05-12T18:51:26.324Z
updated_at: 2026-05-12T20:55:16.185Z
closed_at: 2026-05-12T20:55:16.183Z
close_reason: "Verified against go.dev/ref/mod and go.dev/doc/security: GOFLAGS=-mod=readonly prevents implicit go.mod/go.sum modification (default since Go 1.16 for non-go-get commands). GOSUMDB defaults to sum.golang.org (since Go 1.13). GOPROXY defaults to https://proxy.golang.org,direct. GOPRIVATE sets both GONOSUMDB and GONOPROXY implicitly. go mod verify checks cached modules against go.sum hashes. go mod vendor copies deps to vendor/; go mod verify does NOT check vendored code (confirmed via golang/go#27348, #48420). No discrepancies found in either doc. Citations: go.dev/ref/mod, go.dev/doc/security/best-practices, github.com/golang/go/issues/40728."
---
Verify GOFLAGS=-mod=readonly, GOSUMDB=sum.golang.org default, GOPROXY default, GOPRIVATE behavior, go.sum integrity, vendor mode. Cross-check Go toolchain docs at go.dev.
