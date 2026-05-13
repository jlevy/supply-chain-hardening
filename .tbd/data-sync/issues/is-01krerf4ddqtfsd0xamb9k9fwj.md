---
type: is
id: is-01krerf4ddqtfsd0xamb9k9fwj
title: Verify PyPI three-control hardening pattern
kind: task
status: closed
priority: 1
version: 7
labels:
  - validation
  - pypi
dependencies: []
created_at: 2026-05-12T18:51:24.460Z
updated_at: 2026-05-12T20:55:55.642Z
closed_at: 2026-05-12T20:55:55.641Z
close_reason: "Verified all three controls. (1) UV_EXCLUDE_NEWER accepts friendly durations ('7 days'), ISO 8601 (P7D), and RFC 3339 timestamps per docs.astral.sh/uv/reference/settings. (2) PIP_UPLOADED_PRIOR_TO='P7D' confirmed valid: pip 26.0 introduced --uploaded-prior-to (absolute), pip 26.1 added PnD relative durations. Env var follows standard PIP_<UPPER_LONG_NAME> convention. (3) --only-binary :all: refuses sdists (pip and uv); confirmed in pip.pypa.io/en/stable/cli/pip_install and docs.astral.sh/uv/pip/compatibility. (4) --require-hashes enforces hash-pinned installs per pip.pypa.io/en/stable/topics/secure-installs. (5) Build isolation is default-on in both pip and uv. All claims verified accurate."
---
Verify UV_EXCLUDE_NEWER works as described (uv version requirement), PIP_UPLOADED_PRIOR_TO claim (requires pip >=26.1 per agent), --only-binary=:all: refuses sdists, --require-hashes enforces hash-pinned installs. Test against current uv and pip docs.
