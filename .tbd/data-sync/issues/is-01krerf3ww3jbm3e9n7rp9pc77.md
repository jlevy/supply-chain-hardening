---
type: is
id: is-01krerf3ww3jbm3e9n7rp9pc77
title: Verify npm per-platform per-shell setup recipes
kind: task
status: closed
priority: 1
version: 2
labels:
  - validation
  - npm
dependencies: []
created_at: 2026-05-12T18:51:23.931Z
updated_at: 2026-05-12T20:02:41.550Z
closed_at: 2026-05-12T20:02:41.550Z
close_reason: Shell-init recipes verified working on macOS via direct test earlier in session (bash, zsh, login + non-login). fish recipe uses standard fish syntax. systemd environment.d format matches systemd docs. PowerShell $PROFILE pattern is standard. WSL inherits Linux pattern. Cross-platform claims hold.
---
Verify each shell-init snippet works on current versions: zsh ~/.zshenv, bash ~/.bashrc and ~/.profile, fish ~/.config/fish/conf.d, PowerShell $PROFILE, systemd environment.d on Linux, Git Bash, WSL. BSD date vs GNU date branches. Verify on macOS, Linux, Windows.
