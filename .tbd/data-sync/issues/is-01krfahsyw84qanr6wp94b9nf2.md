---
type: is
id: is-01krfahsyw84qanr6wp94b9nf2
title: Improve verification commands to prove env vars are actually active
kind: task
status: closed
priority: 2
version: 3
labels:
  - docs
  - verification
dependencies: []
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:07:26.428Z
updated_at: 2026-05-13T01:36:28.550Z
closed_at: 2026-05-13T01:36:28.545Z
close_reason: |-
  Improved verify sections across hardening-npm.md, hardening-pypi.md, and hardening-go.md to use 'env | grep' for shell-state checks alongside the tool-specific config-get commands. Added explicit note in npm and pypi guides that env-var-only setups are not visible to GUI-launched agents / non-interactive subprocesses and that confirmation should happen in the agent's own process. PyPI guide also gained a behaviour-based dry-run check (uv pip install --dry-run against a known sdist-only package should fail under UV_NO_BUILD) earlier under sch-oaei. Go guide notes the difference between shell env and AR='ar'
  CC='cc'
  CGO_CFLAGS='-O2 -g'
  CGO_CPPFLAGS=''
  CGO_CXXFLAGS='-O2 -g'
  CGO_ENABLED='1'
  CGO_FFLAGS='-O2 -g'
  CGO_LDFLAGS='-O2 -g'
  CXX='c++'
  GCCGO='gccgo'
  GO111MODULE=''
  GOARCH='arm64'
  GOARM64='v8.0'
  GOAUTH='netrc'
  GOBIN=''
  GOCACHE='/Users/levy/Library/Caches/go-build'
  GOCACHEPROG=''
  GODEBUG=''
  GOENV='/Users/levy/Library/Application Support/go/env'
  GOEXE=''
  GOEXPERIMENT=''
  GOFIPS140='off'
  GOFLAGS=''
  GOGCCFLAGS='-fPIC -arch arm64 -pthread -fno-caret-diagnostics -Qunused-arguments -fmessage-length=0 -ffile-prefix-map=/var/folders/ms/fjn8hgyd24d3jv6w65dw37hh0000gp/T/go-build312874446=/tmp/go-build -gno-record-gcc-switches -fno-common'
  GOHOSTARCH='arm64'
  GOHOSTOS='darwin'
  GOINSECURE=''
  GOMOD='/dev/null'
  GOMODCACHE='/Users/levy/wrk/gowork/pkg/mod'
  GONOPROXY=''
  GONOSUMDB=''
  GOOS='darwin'
  GOPATH='/Users/levy/wrk/gowork'
  GOPRIVATE=''
  GOPROXY='https://proxy.golang.org,direct'
  GOROOT='/opt/homebrew/Cellar/go/1.24.3/libexec'
  GOSUMDB='sum.golang.org'
  GOTELEMETRY='local'
  GOTELEMETRYDIR='/Users/levy/Library/Application Support/go/telemetry'
  GOTMPDIR=''
  GOTOOLCHAIN='auto'
  GOTOOLDIR='/opt/homebrew/Cellar/go/1.24.3/libexec/pkg/tool/darwin_arm64'
  GOVCS=''
  GOVERSION='go1.24.3'
  GOWORK=''
  PKG_CONFIG='pkg-config' persisted config.
---
# Improve verification commands to prove env vars are actually active

## Problem

The current "Step 3: Verify" sections (in hardening-pypi.md, hardening-npm.md,
hardening-go.md) check things like `pip config get global.only-binary`,
`pnpm config get before`, etc. These can be misleading:

- `pip config get global.only-binary` reads from pip's config files, not env
  vars. It returns nothing if the value is only set via PIP_ONLY_BINARY.
- An empty-string env var may not always behave the same as an unset env var.
- `echo "$VAR"` confirms shell state but not that the subprocess actually
  honored the value (especially for non-interactive agents or GUI-launched
  processes that may not inherit shell state).

Reviewer is right that the verification commands can give false confidence.

## Fix

Replace per-ecosystem verify steps with a two-tier check:

1. Cheap shell check: `echo` each variable plus print which file sourced it
   (use `set -x; . ~/.npm-hardening.sh; set +x` snippet in docs, or
   suggest `env | grep ^NPM_CONFIG_`).
2. Behavior check: a controlled command that should fail under the
   hardening:
   - npm/pnpm: try `pnpm add some-very-fresh-package@<latest>` against a
     known-fresh test package or a future date, expect failure due to
     `before`/`minimum-release-age`. Alternatively, `pnpm add --dry-run` with
     a freshly-published test target.
   - PyPI: `uv pip install --dry-run` against a known sdist-only test
     package; expect failure under UV_NO_BUILD.
   - Go: `go mod download` of an unknown module should fail under
     `-mod=readonly` if it would change go.mod.

Also add a note: env-var-only setups are not visible to GUI-launched agents
or non-interactive subprocesses unless those processes inherit the shell
environment. Suggest checking with `env | grep NPM_CONFIG_BEFORE` *from
inside the agent's shell*, not just from a terminal.

## Files to edit

- guidelines/hardening-npm.md
- guidelines/hardening-pypi.md
- guidelines/hardening-go.md
- guidelines/hardening-crates.md (for `cargo` alias check)

## Acceptance

- Verify section proves the env var is active rather than just printing it.
- A reader who follows the verify step and gets the expected failure has
  high confidence the control works.
- A note warns that aliases / shell init only protect interactive shells;
  for agents, recommend an explicit env-var dump in the agent's shell.
