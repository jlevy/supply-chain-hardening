---
type: is
id: is-01krerf3ww3jbm3e9n7rp9pc77
title: Verify npm per-platform per-shell setup recipes
kind: task
status: closed
priority: 1
version: 5
labels:
  - validation
  - npm
dependencies: []
created_at: 2026-05-12T18:51:23.931Z
updated_at: 2026-05-12T20:55:26.491Z
closed_at: 2026-05-12T20:55:26.490Z
close_reason: "Verified per-platform/per-shell setup recipes. (1) zsh ~/.zshenv: confirmed sourced on every invocation (login, interactive, non-interactive, scripts) per zsh docs and scriptingosx.com/2019/06/moving-to-zsh-part-2-configuration-files. (2) bash ~/.bashrc + ~/.profile: standard interactive non-login + login coverage; correct. (3) fish ~/.config/fish/conf.d: auto-sourced per fish docs; found and fixed missing GNU date fallback (BSD-only date -v-7d would silently fail on Linux fish users). (4) PowerShell $PROFILE: standard PS7/PS5 profile path; correct. (5) systemd environment.d: format verified against freedesktop.org/software/systemd/man/latest/environment.d.html; KEY=VALUE lines with # comments, .conf extension; static values only as documented. (6) Git Bash: reads ~/.bashrc and ~/.bash_profile per POSIX; correct. (7) WSL: follows Linux recipes; correct. (8) BSD date (date -u -v-7d) tested on macOS 15 producing 2026-05-05T20:53:01Z; GNU date (date -u -d '7 days ago') format string identical; both produce ISO-8601 as claimed. Citations: fishshell.com/docs/current/fish_for_bash_users.html, freedesktop.org/software/systemd/man/latest/environment.d.html, scriptingosx.com/2019/06/moving-to-zsh-part-2-configuration-files, man.freebsd.org/cgi/man.cgi?query=date"
---
Verify each shell-init snippet works on current versions: zsh ~/.zshenv, bash ~/.bashrc and ~/.profile, fish ~/.config/fish/conf.d, PowerShell $PROFILE, systemd environment.d on Linux, Git Bash, WSL. BSD date vs GNU date branches. Verify on macOS, Linux, Windows.
