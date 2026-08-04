# Untrusted Repo First Run

**Last updated:** 2026-08-04

**Author:** Joshua Levy (github.com/jlevy) with agent assistance

Before you run `install`, `build`, or `test` on a freshly cloned third-party repo, treat
it as untrusted code.
Install scripts, source distributions, `build.rs`, proc-macros, test files, and ordinary
import-time code execute on your machine with your ambient credentials.
The 2025-2026 wave (Shai-Hulud, TanStack, Mini Shai-Hulud, mysten-metrics,
guardrails-ai, LiteLLM) routinely targeted exactly this moment.

> [!WARNING]
> **Opening the repo is now part of the risky step, not the safe preamble.** From April
> 2026, campaigns commit editor and agent config that executes on folder open: the June
> 2026 Miasma commits to `Azure/durabletask` planted a `.claude/settings.json`
> `SessionStart` hook, and the August 2026 keyv worm wrote both that and a
> `.vscode/tasks.json` `folderOpen` task.
> Cloning remains safe.
> Do the triage in [`hardening-agent-workspaces.md`](hardening-agent-workspaces.md) →
> “Triage Before You Open” before the repo reaches an editor or an agent, then come back
> here before running anything.

## The Rule

Do not open in an editor or agent, and do not run `install`, `build`, `test`, `run`,
`dlx`, `npx`, `bunx`, `uvx`, `go run`, `cargo run`, `cargo build`, `cargo install`, or
any equivalent command for an untrusted repo on a machine that has any of:

- cloud credentials (`~/.aws`, `~/.config/gcloud`, `~/.azure`, `~/.kube`, `~/.docker`)
- SSH keys (`~/.ssh`, `~/.gnupg`)
- registry publish tokens (`~/.npmrc` with `_authToken`, `~/.pypirc`,
  `~/.cargo/credentials.toml`, `~/.config/gh`)
- writable production access (browser sessions, password manager unlocked, VPN connected
  to production)
- a clipboard with sensitive content

Either move the work into a sandbox that has none of those, or read the entire repo end
to end before running anything in it.

## Minimal Sandbox Recipes

### Docker (Recommended; Cross-Platform)

Cleanest blast-radius isolation for the cost of pulling an image once.

```sh
# From the parent directory of the cloned repo. Replace REPO with the directory name.
docker run --rm -it \
  --network=none \
  --user "$(id -u):$(id -g)" \
  -v "$PWD/REPO:/work:ro" \
  -w /work \
  --tmpfs /tmp:exec,size=512m \
  -e HOME=/tmp \
  node:22-slim    # or python:3.13-slim, rust:1.83, golang:1.26
```

Notes:

- `--network=none` is the aggressive default; many installs need network access.
  If so, replace with a restricted egress policy that only allows the registry the repo
  declares (e.g. `registry.npmjs.org`, `pypi.org`, `crates.io`, `proxy.golang.org`).
- The read-only mount (`:ro`) prevents the container from mutating your source tree.
  Add a writable mount under `/work/.cache` or similar if the toolchain needs it.
- `HOME=/tmp` keeps the container from probing your real `~/.npmrc` etc., even by
  accident.
- For npm/pnpm: also set `NPM_CONFIG_IGNORE_SCRIPTS=true` inside the container as a
  belt-and-braces.

### macOS Sandbox Profile (`sandbox-exec`)

Lighter weight; not a security boundary as strong as a container, but useful when you
cannot pull an image.

```sh
cat > /tmp/repo-sandbox.sb <<'EOF'
(version 1)
(deny default)
(allow process-fork)
(allow process-exec)
(allow file-read*)
(allow file-write* (subpath (param "REPO")))
(allow file-write* (subpath "/tmp"))
(allow file-write* (subpath "/private/tmp"))
(allow network*)   ; tighten to specific hosts if you can
EOF
sandbox-exec -f /tmp/repo-sandbox.sb -D REPO="$PWD/REPO" \
  env HOME=/tmp PATH=/usr/bin:/bin npm install
```

### Linux `unshare` / User Namespaces

```sh
# Strip network and mount tmpfs over $HOME so credentials are not visible to the child.
unshare --user --net --mount sh -c '
  mount -t tmpfs tmpfs $HOME
  cd /path/to/REPO
  npm install --ignore-scripts
'
```

Caveats: `unshare --user` requires kernel support; the network namespace has no default
route, so you may need to add a tightly-scoped veth pair if the install needs network.

## What To Strip From the Sandbox

Confirm none of the following are present inside the sandbox:

- [ ] No cloud credentials (`~/.aws`, `~/.config/gcloud`, `~/.azure`, `~/.kube`)
- [ ] No SSH keys (`~/.ssh`)
- [ ] No GPG keys (`~/.gnupg`)
- [ ] No registry publish tokens (`~/.npmrc` `_authToken`, `~/.pypirc`,
  `~/.cargo/credentials.toml`)
- [ ] No GitHub auth (`~/.config/gh`)
- [ ] No git committer identity that could be forged (clean `~/.gitconfig` or none)
- [ ] No clipboard content (sandbox does not need clipboard access)
- [ ] Network egress restricted to the explicit registry the repo declares, or `none`

## Per-Ecosystem: What Actually Executes On First Run

| Ecosystem | What runs at install / build / test | Mitigation (still: do it in a sandbox) |
| --- | --- | --- |
| npm / pnpm | `preinstall`, `install`, `postinstall`, `prepare`, `prepublish` scripts; implicit `node-gyp` builds driven by `binding.gyp`, which Miasma wave 2 used to evade lifecycle-script monitoring | `NPM_CONFIG_IGNORE_SCRIPTS=true`; npm 12 blocks dependency lifecycle scripts and implicit `node-gyp` builds by default |
| Python (sdist) | `setup.py`, `setup.cfg`, PEP 517 build backend at `pip install` / `uv pip install` | `PIP_ONLY_BINARY=:all:`; uv `--no-build` per command (don’t export a blanket `UV_NO_BUILD`, it breaks `uv sync` of the repo’s own package) |
| Python (wheel) | Module top-level code at `import` time. **Also `.pth` files at every interpreter startup**, with no import and no build, which is how the June 2026 Hades campaign ran | No install-time control stops either. Audit `.pth` files (`hardening-pypi.md` → Step 5); isolate at import |
| Rust | `build.rs` at any `cargo build`, `cargo check`, `cargo test`, or `cargo run`; proc-macros at compile time | No flag disables `build.rs`; read it, or build in a sandbox |
| Go | Test files at any `go test ./...`. No install-time hooks; `go build` itself does not run module code | `-mod=readonly` does not stop test execution; use sandbox for tests |
| Any (editor / agent) | `.vscode/tasks.json` `folderOpen` tasks, `.claude/settings.json` hooks, `.devcontainer` lifecycle commands, `.mcp.json` servers, at **folder open** | Workspace trust plus a pre-open review; see [`hardening-agent-workspaces.md`](hardening-agent-workspaces.md) |

## When To Skip the Sandbox

Skipping is reasonable if **all** of the following hold:

- The repo is from a project you have collaborated with directly and you have read the
  recent commit history.
- The exact version / commit is pinned and reviewed.
- You are inside the cool-off window for any newly-published dependencies.
- You will run only the build, not third-party scripts.

For agent workflows, default to never skipping: the cost of one container start is
small; the cost of one credential exfiltration is not.

## Pointers

- [`hardening-agent-workspaces.md`](hardening-agent-workspaces.md): the open-time
  counterpart to this file, for the moment before you run anything.
- [`SUPPLY-CHAIN-SECURITY.md`](../SUPPLY-CHAIN-SECURITY.md): the portable agent rule
  that points back to this procedure.
- [`AGENTS.md`](../AGENTS.md): “Safety Rule For Agents” references this file.
- Per-ecosystem playbooks ([`hardening-npm.md`](hardening-npm.md),
  [`hardening-pypi.md`](hardening-pypi.md),
  [`hardening-crates.md`](hardening-crates.md), [`hardening-go.md`](hardening-go.md)):
  each lists the install-time risks that this sandbox blunts.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
