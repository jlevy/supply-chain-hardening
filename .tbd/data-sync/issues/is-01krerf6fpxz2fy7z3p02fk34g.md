---
type: is
id: is-01krerf6fpxz2fy7z3p02fk34g
title: Verify Go platform-specific setup
kind: task
status: closed
priority: 1
version: 5
labels:
  - validation
  - go
dependencies: []
created_at: 2026-05-12T18:51:26.581Z
updated_at: 2026-05-12T20:55:27.928Z
closed_at: 2026-05-12T20:55:27.927Z
close_reason: "Verified all platform-specific setup recipes. macOS: zsh (default since 10.15) via ~/.zshenv, bash interactive via ~/.bashrc, bash login via ~/.bash_profile, fish via conf.d. Linux: same shell patterns plus systemd user env via ~/.config/environment.d/go-hardening.conf. Windows: PowerShell 7 via $PROFILE, persistent user-wide via [Environment]::SetEnvironmentVariable, Git Bash sources ~/.go-hardening.sh, WSL follows Linux. Go env vars are portable across all platforms. Workspace mode (go.work) section accurately describes Go 1.18+ use directives and trust implications paralleling replace directives. No discrepancies. Citations: go.dev/doc/tutorial/workspaces, go.googlesource.com/proposal/+/master/design/45713-workspace.md."
---
Verify Go env-var and toolchain commands work on macOS, Linux, Windows. Check workspace mode.
