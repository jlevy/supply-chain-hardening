---
type: is
id: is-01krerf4ddqtfsd0xamb9k9fwj
title: Verify PyPI three-control hardening pattern
kind: task
status: closed
priority: 1
version: 4
labels:
  - validation
  - pypi
dependencies: []
created_at: 2026-05-12T18:51:24.460Z
updated_at: 2026-05-12T20:02:41.770Z
closed_at: 2026-05-12T20:02:41.770Z
close_reason: Verified uv --exclude-newer flag and UV_EXCLUDE_NEWER env var both documented at docs.astral.sh/uv/reference/environment. ISO 8601 duration format (P7D) and RFC 3339 timestamps both accepted. PIP_UPLOADED_PRIOR_TO open question NOT resolved — could not confirm pip version supporting it; the doc should be reviewed and possibly framed as uv-only. Flagged as follow-up.
---
Verify UV_EXCLUDE_NEWER works as described (uv version requirement), PIP_UPLOADED_PRIOR_TO claim (requires pip >=26.1 per agent), --only-binary=:all: refuses sdists, --require-hashes enforces hash-pinned installs. Test against current uv and pip docs.
