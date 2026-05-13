---
type: is
id: is-01krerf4nf8k6rzp9zxp925f0s
title: Verify PyPI per-platform per-shell setup recipes
kind: task
status: closed
priority: 1
version: 5
labels:
  - validation
  - pypi
dependencies: []
created_at: 2026-05-12T18:51:24.718Z
updated_at: 2026-05-12T20:56:14.491Z
closed_at: 2026-05-12T20:56:14.490Z
close_reason: "Verified all platform/shell recipes. macOS zsh (~/.zshenv), bash (~/.bashrc + ~/.bash_profile), fish (~/.config/fish/conf.d/): all correct for sourcing POSIX or reproducing exports. Linux bash, zsh, fish: same patterns, correct. systemd environment.d snippet: correct format (KEY=value, no 'export'). Windows PowerShell 5/7 ($PROFILE $env:VAR), persistent registry ([Environment]::SetEnvironmentVariable), cmd (setx), Git Bash (~/.bashrc), WSL (Linux recipes): all verified. CI snippets (GitHub Actions env block, GitLab CI variables block): correct. UV_EXCLUDE_NEWER='7 days' and PIP_UPLOADED_PRIOR_TO='P7D' both use correct format per tool docs. No ISO 8601 P7D date arithmetic needed for uv (friendly format); pip accepts PnD natively in 26.1+."
---
Verify each shell-init snippet for pip/uv across macOS, Linux, Windows. Verify systemd environment.d snippet. PowerShell snippet. CI snippets for GitHub Actions and GitLab CI.
