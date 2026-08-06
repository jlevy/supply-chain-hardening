---
type: is
id: is-01kz7fs5zy2f70ye7md6cpws54
title: "Upgrade tbd to v0.4.2 (documented cool-off exception: first-party, self-audited)"
kind: chore
status: closed
priority: 0
version: 2
labels:
  - tooling
dependencies: []
parent_id: is-01kz7f5sfqpzcjr0vnz1dk2qs1
created_at: 2026-08-04T22:54:48.318Z
updated_at: 2026-08-04T22:56:40.608Z
closed_at: 2026-08-04T22:56:40.608Z
close_reason: "tbd 0.4.2 installed and verified: integrity sha512 + shasum match registry, SLSA provenance present, published via GitHub Actions OIDC from jlevy/tbd, maintainer ojoshe. Age 5 days = inside 14-day cool-off; user-authorized first-party exception. tbd setup --auto migrated config f03->f06."
---
User-approved exception to the 14-day cool-off: get-tbd is first-party and already audited. Audit it locally anyway (publisher, publish time, integrity), install, run tbd setup, and record the exception in the repo's own audit-log format since this repo's README requires exceptions to be on the record.
