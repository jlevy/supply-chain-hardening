---
type: is
id: is-01kz7m5vxmt4cwvzd4f51bt2hb
title: "VERIFY: user-level config file paths and set-commands for all 6 tools"
kind: task
status: closed
priority: 0
version: 2
labels:
  - research
dependencies: []
parent_id: is-01kz7m5v8k3y8kvwdkqn6gw87g
created_at: 2026-08-05T00:11:38.292Z
updated_at: 2026-08-05T00:12:41.443Z
closed_at: 2026-08-05T00:12:41.442Z
close_reason: "Verified user-level config: npm ~/.npmrc (npm config set --location=user); pnpm ~/.config/pnpm/config.yaml; Yarn ~/.yarnrc.yml (yarn config set --home); Bun ~/.bunfig.toml BUT global is silently ignored by bun add; uv ~/.config/uv/uv.toml (macOS/Linux) / %APPDATA%\\uv\\uv.toml, precedence CLI > env > PROJECT > user > system, so project config overrides user config and only the env var is repo-proof. Also found bunx accepts --minimum-release-age as a no-op (oven-sh/bun#30748)."
---
