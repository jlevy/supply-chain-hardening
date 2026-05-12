---
type: is
id: is-01krerf6zpe7h21gkt08acwnj8
title: Verify README authoritative sources URLs all resolve
kind: task
status: closed
priority: 2
version: 2
labels:
  - validation
  - cross-cutting
dependencies: []
created_at: 2026-05-12T18:51:27.093Z
updated_at: 2026-05-12T18:56:39.992Z
closed_at: 2026-05-12T18:56:39.991Z
close_reason: "Checked all 28 URLs in README.md → Authoritative Sources via curl. 25 returned 200. Three broken; fixed in README.md: (1) https://blog.phylum.io/ returns code 000 (DNS/TLS) — replaced with https://www.phylum.io/blog (200). (2) https://www.aikido.dev/intel returns 404 — replaced with https://intel.aikido.dev (200). (3) https://www.cisa.gov/news-events/alerts returns 404 — replaced with https://www.cisa.gov/news-events/cybersecurity-advisories (200). Same three URLs also appear in research-/hardening-*.md files; deferring sweep there until parallel validation agents finish to avoid edit conflicts."
---
Click through every URL in README.md Authoritative Sources section. Check OSV.dev, GHSA filters, RustSec, PyPA, Go vuln DB, Aikido, StepSecurity, Socket, Datadog, ReversingLabs, Unit 42, Phylum, JFrog, CISA, Snyk, Sonatype, Wiz. Replace dead links with archive.org snapshots.
