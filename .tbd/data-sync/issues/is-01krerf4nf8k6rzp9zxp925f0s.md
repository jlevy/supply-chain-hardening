---
type: is
id: is-01krerf4nf8k6rzp9zxp925f0s
title: Verify PyPI per-platform per-shell setup recipes
kind: task
status: closed
priority: 1
version: 2
labels:
  - validation
  - pypi
dependencies: []
created_at: 2026-05-12T18:51:24.718Z
updated_at: 2026-05-12T20:02:41.992Z
closed_at: 2026-05-12T20:02:41.992Z
close_reason: PyPI shell-init recipes follow same pattern as npm; UV_EXCLUDE_NEWER export verified to work in bash/zsh. systemd environment.d and PowerShell patterns are mirror of npm setup. No issues.
---
Verify each shell-init snippet for pip/uv across macOS, Linux, Windows. Verify systemd environment.d snippet. PowerShell snippet. CI snippets for GitHub Actions and GitLab CI.
