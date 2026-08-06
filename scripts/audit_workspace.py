#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
#
# audit_workspace.py
#
# Audit a repository and the local host for *open-time* and *load-time*
# supply-chain persistence: payloads that execute when a developer or AI agent
# opens a workspace, or on every Python interpreter start, rather than at
# package-install time.
#
# The install-side controls documented elsewhere in this repo (release-age
# cool-off, ignore-scripts, --only-binary, frozen lockfiles) do not apply to
# these vectors, because the payload arrives in a git repository or inside an
# already-installed wheel rather than as a fresh registry publish.
#
# Four independent checks:
#
#     autostart  Editor and agent configs that execute a command on open
#                (.vscode/tasks.json runOn:folderOpen, .claude/settings.json
#                and .codex/hooks.json hooks, .devcontainer postCreateCommand,
#                .mcp.json)
#     unicode    Invisible / bidirectional Unicode in agent instruction files
#                (CLAUDE.md, AGENTS.md, .cursorrules), the TrapDoor vector
#     pth        Python .pth files that execute code at interpreter startup,
#                the Hades vector (runs without importing the package)
#     host       Known host-level persistence from the 2026-08-04 keyv worm
#
# This script is deliberately written in Python (stdlib only) so the audit tool
# does not ride on the same supply chain it audits, and so a single invocation
# works identically on macOS, Linux, and Windows. It is read-only: it never
# deletes, edits, or executes anything it finds.
#
# Run with one of:
#     uv run scripts/audit_workspace.py [PATH]     # preferred: hermetic Python
#     python3 scripts/audit_workspace.py [PATH]    # fallback: system Python
#
# Documentation: ./README.md
# Guideline:     ../guidelines/hardening-agent-workspaces.md
#
# Exit codes:
#     0  no findings
#     1  informational findings only (review, likely benign)
#     2  error (bad arguments, unreadable target)
#     3  one or more HIGH findings (treat as compromise until disproven)

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

# Invisible and direction-controlling code points. Zero-width characters hide
# injected agent instructions in plain sight; bidi overrides can reorder how a
# line renders versus how it parses.
INVISIBLE_CODEPOINTS = frozenset(
    {
        0x00AD,  # SOFT HYPHEN
        0x200B,  # ZERO WIDTH SPACE
        0x200C,  # ZERO WIDTH NON-JOINER
        0x200D,  # ZERO WIDTH JOINER
        0x200E,  # LEFT-TO-RIGHT MARK
        0x200F,  # RIGHT-TO-LEFT MARK
        0x202A,  # LEFT-TO-RIGHT EMBEDDING
        0x202B,  # RIGHT-TO-LEFT EMBEDDING
        0x202C,  # POP DIRECTIONAL FORMATTING
        0x202D,  # LEFT-TO-RIGHT OVERRIDE
        0x202E,  # RIGHT-TO-LEFT OVERRIDE
        0x2060,  # WORD JOINER
        0x2066,  # LEFT-TO-RIGHT ISOLATE
        0x2067,  # RIGHT-TO-LEFT ISOLATE
        0x2068,  # FIRST STRONG ISOLATE
        0x2069,  # POP DIRECTIONAL ISOLATE
        0xFEFF,  # ZERO WIDTH NO-BREAK SPACE (BOM when leading)
    }
)

# Files an AI coding agent reads as trusted instructions. Content here steers the
# agent using its own already-granted permissions, so it needs no execution
# primitive of its own.
AGENT_INSTRUCTION_FILES = (
    "CLAUDE.md",
    "AGENTS.md",
    "GEMINI.md",
    ".cursorrules",
    ".clinerules",
    ".windsurfrules",
    ".github/copilot-instructions.md",
)

AGENT_INSTRUCTION_GLOBS = (
    ".cursor/rules/*.mdc",
    ".claude/commands/*.md",
    ".claude/agents/*.md",
    ".claude/skills/**/*.md",
    ".agents/**/*.md",  # cross-agent skills convention, e.g. .agents/skills/*/SKILL.md
)

# devcontainer.json keys that run a shell command as part of opening the folder.
DEVCONTAINER_COMMAND_KEYS = (
    "initializeCommand",
    "onCreateCommand",
    "updateContentCommand",
    "postCreateCommand",
    "postStartCommand",
    "postAttachCommand",
)

# Host persistence written by the 2026-08-04 keyv / cacheable worm. The watcher
# polls GitHub and evaluates an operator-supplied handler when the stolen token
# stops working, so revoking credentials before removing it is the trigger.
KEYV_HOST_ARTIFACTS = (
    "~/.config/gh-token-monitor/token",
    "~/.config/gh-token-monitor/handler",
    "~/.config/gh-token-monitor/started_at",
    "~/.local/bin/gh-token-monitor.sh",
    "~/Library/LaunchAgents/com.user.gh-token-monitor.plist",
    "~/.config/systemd/user/gh-token-monitor.service",
    "/tmp/gh-token-monitor.out.log",
    "/tmp/gh-token-monitor.err.log",
)

# In-repo payload filenames from the keyv worm and TrapDoor.
KNOWN_PAYLOAD_FILENAMES = frozenset(
    {"setup.mjs", "Math_Symbol.js", "math_init.js", "_index.js", "trap-core.js"}
)

# A legitimate .pth file contains only paths and blank/comment lines. Python
# executes any line beginning with "import" at interpreter startup, which is the
# whole mechanism the Hades campaign abused.
PTH_ALLOWLIST_PREFIXES = (
    "distutils-precedence.pth",  # setuptools
    "__editable__",  # PEP 660 editable installs
)

DIRS_TO_SKIP = frozenset({".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"})

SEVERITY_HIGH = "HIGH"
SEVERITY_INFO = "INFO"


@dataclass(frozen=True)
class Finding:
    check: str
    severity: str
    path: str
    detail: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def read_text(path: Path) -> str | None:
    """Read a file as UTF-8, returning None for binaries and unreadable files."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def load_jsonc(text: str) -> object | None:
    """Parse JSON that may contain // and /* */ comments and trailing commas,
    as VS Code allows in its JSONC config files.

    Strips comments and trailing commas outside string literals, then falls
    back to None if the result still does not parse. A config we cannot parse
    is reported by the caller rather than silently skipped. Trailing commas
    matter: a malicious tasks.json that is valid JSONC but not strict JSON
    must not downgrade from a HIGH autostart finding to an INFO parse failure.
    """
    out: list[str] = []
    in_string = False
    in_line_comment = False
    in_block_comment = False
    escaped = False
    i = 0
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
                out.append(ch)
        elif in_block_comment:
            if ch == "*" and nxt == "/":
                in_block_comment = False
                i += 1
        elif in_string:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        else:
            if ch == "/" and nxt == "/":
                in_line_comment = True
                i += 1
            elif ch == "/" and nxt == "*":
                in_block_comment = True
                i += 1
            else:
                if ch == '"':
                    in_string = True
                elif ch in "}]":
                    # Drop a comma directly preceding this closer (with only
                    # whitespace between): the JSONC trailing comma.
                    j = len(out) - 1
                    while j >= 0 and out[j] in " \t\r\n":
                        j -= 1
                    if j >= 0 and out[j] == ",":
                        del out[j]
                out.append(ch)
        i += 1
    try:
        return json.loads("".join(out))
    except json.JSONDecodeError:
        return None


def walk_files(root: Path):
    """Yield files under root, skipping vendored and VCS-internal trees."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in DIRS_TO_SKIP]
        for name in filenames:
            yield Path(dirpath) / name


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# Check: autostart configuration
# ---------------------------------------------------------------------------


def check_autostart(root: Path) -> list[Finding]:
    findings: list[Finding] = []

    tasks_path = root / ".vscode" / "tasks.json"
    if tasks_path.is_file():
        text = read_text(tasks_path)
        data = load_jsonc(text) if text else None
        if data is None:
            findings.append(
                Finding(
                    "autostart",
                    SEVERITY_INFO,
                    rel(tasks_path, root),
                    "present but could not be parsed; read it by hand",
                )
            )
        elif isinstance(data, dict):
            for task in data.get("tasks", []) or []:
                if not isinstance(task, dict):
                    continue
                run_on = (task.get("runOptions") or {}).get("runOn")
                if run_on == "folderOpen":
                    command = task.get("command", "(no command field)")
                    args = task.get("args") or []
                    if args:
                        command = f"{command} {' '.join(str(a) for a in args)}"
                    findings.append(
                        Finding(
                            "autostart",
                            SEVERITY_HIGH,
                            rel(tasks_path, root),
                            f'runOn:folderOpen task "{task.get("label", "?")}" executes: {command}',
                        )
                    )

    # Codex CLI reads the same hooks schema from .codex/hooks.json, so one loop
    # covers both agents; the permissions block simply never appears for Codex.
    agent_settings_paths = (
        root / ".claude" / "settings.json",
        root / ".claude" / "settings.local.json",
        root / ".codex" / "hooks.json",
    )
    for settings_path in agent_settings_paths:
        if not settings_path.is_file():
            continue
        text = read_text(settings_path)
        data = load_jsonc(text) if text else None
        if data is None:
            findings.append(
                Finding(
                    "autostart",
                    SEVERITY_INFO,
                    rel(settings_path, root),
                    "present but could not be parsed; read it by hand",
                )
            )
            continue
        if not isinstance(data, dict):
            continue
        hooks = data.get("hooks")
        if isinstance(hooks, dict):
            for event, entries in hooks.items():
                for command in extract_hook_commands(entries):
                    findings.append(
                        Finding(
                            "autostart",
                            SEVERITY_HIGH,
                            rel(settings_path, root),
                            f"{event} hook executes: {command}",
                        )
                    )
        allow = (data.get("permissions") or {}).get("allow") if isinstance(data.get("permissions"), dict) else None
        if allow:
            findings.append(
                Finding(
                    "autostart",
                    SEVERITY_INFO,
                    rel(settings_path, root),
                    f"repo-supplied permissions.allow widens agent authority: {allow}",
                )
            )

    mcp_path = root / ".mcp.json"
    if mcp_path.is_file():
        text = read_text(mcp_path)
        data = load_jsonc(text) if text else None
        if isinstance(data, dict):
            for name, server in (data.get("mcpServers") or {}).items():
                if not isinstance(server, dict):
                    continue
                command = server.get("command") or server.get("url") or "(unknown)"
                args = server.get("args") or []
                if args:
                    command = f"{command} {' '.join(str(a) for a in args)}"
                findings.append(
                    Finding(
                        "autostart",
                        SEVERITY_INFO,
                        rel(mcp_path, root),
                        f'MCP server "{name}" launches: {command}',
                    )
                )

    devcontainer_candidates = [
        root / ".devcontainer" / "devcontainer.json",
        root / ".devcontainer.json",
    ]
    devcontainer_candidates.extend(sorted(root.glob(".devcontainer/*/devcontainer.json")))
    for dc_path in devcontainer_candidates:
        if not dc_path.is_file():
            continue
        text = read_text(dc_path)
        data = load_jsonc(text) if text else None
        if not isinstance(data, dict):
            continue
        for key in DEVCONTAINER_COMMAND_KEYS:
            if key in data:
                findings.append(
                    Finding(
                        "autostart",
                        SEVERITY_HIGH,
                        rel(dc_path, root),
                        f"{key} executes: {data[key]}",
                    )
                )

    envrc = root / ".envrc"
    if envrc.is_file():
        findings.append(
            Finding(
                "autostart",
                SEVERITY_INFO,
                rel(envrc, root),
                "direnv executes this on cd if the directory is allowed; read before `direnv allow`",
            )
        )

    for path in walk_files(root):
        if path.name in KNOWN_PAYLOAD_FILENAMES:
            findings.append(
                Finding(
                    "autostart",
                    SEVERITY_HIGH,
                    rel(path, root),
                    "filename matches a known 2026 loader payload (keyv worm / TrapDoor)",
                )
            )

    return findings


def extract_hook_commands(entries: object) -> list[str]:
    """Pull command strings out of a Claude Code hooks entry, whatever its shape."""
    commands: list[str] = []
    if isinstance(entries, list):
        for entry in entries:
            commands.extend(extract_hook_commands(entry))
    elif isinstance(entries, dict):
        if "command" in entries and isinstance(entries["command"], str):
            commands.append(entries["command"])
        for value in entries.values():
            if isinstance(value, (list, dict)):
                commands.extend(extract_hook_commands(value))
    return commands


# ---------------------------------------------------------------------------
# Check: invisible Unicode in agent instruction files
# ---------------------------------------------------------------------------


def check_unicode(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    candidates: list[Path] = []

    for name in AGENT_INSTRUCTION_FILES:
        candidates.append(root / name)
    for pattern in AGENT_INSTRUCTION_GLOBS:
        candidates.extend(sorted(root.glob(pattern)))
    # Nested CLAUDE.md / AGENTS.md files anywhere in the tree.
    for path in walk_files(root):
        if path.name in {"CLAUDE.md", "AGENTS.md", "GEMINI.md", ".cursorrules"}:
            candidates.append(path)

    seen: set[Path] = set()
    for path in candidates:
        resolved = path.resolve()
        if resolved in seen or not path.is_file():
            continue
        seen.add(resolved)
        text = read_text(path)
        if text is None:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            hits = sorted({ord(c) for c in line if ord(c) in INVISIBLE_CODEPOINTS})
            # A BOM as the very first character of the file is ordinary.
            if hits == [0xFEFF] and lineno == 1 and line.startswith("﻿"):
                if not any(ord(c) in INVISIBLE_CODEPOINTS for c in line[1:]):
                    continue
            if hits:
                names = ", ".join(f"U+{cp:04X}" for cp in hits)
                findings.append(
                    Finding(
                        "unicode",
                        SEVERITY_HIGH,
                        f"{rel(path, root)}:{lineno}",
                        f"invisible/bidi code points in agent instruction file: {names}",
                    )
                )

    return findings


# ---------------------------------------------------------------------------
# Check: .pth interpreter startup hooks
# ---------------------------------------------------------------------------


def site_package_dirs() -> list[Path]:
    dirs: list[Path] = []
    try:
        import site

        for entry in site.getsitepackages():
            dirs.append(Path(entry))
        user_site = site.getusersitepackages()
        if isinstance(user_site, str):
            dirs.append(Path(user_site))
    except Exception:
        pass
    return [d for d in dirs if d.is_dir()]


def check_pth(root: Path, scan_site: bool) -> list[Finding]:
    findings: list[Finding] = []

    search_dirs: list[Path] = [root]
    if scan_site:
        search_dirs.extend(site_package_dirs())

    seen: set[Path] = set()
    for base in search_dirs:
        for path in walk_files(base):
            if path.suffix != ".pth":
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            text = read_text(path)
            if text is None:
                continue
            # Match site.py's semantics exactly: CPython tests the RAW line
            # (no strip), so an indented "import" is a path entry that never
            # executes. Stripping here would flag lines Python ignores.
            executable_lines = [
                line
                for line in text.splitlines()
                if line.startswith(("import ", "import\t"))
            ]
            if not executable_lines:
                continue
            allowlisted = any(path.name.startswith(p) for p in PTH_ALLOWLIST_PREFIXES)
            severity = SEVERITY_INFO if allowlisted else SEVERITY_HIGH
            note = " (known-good setuptools/editable hook)" if allowlisted else ""
            findings.append(
                Finding(
                    "pth",
                    severity,
                    str(path),
                    f"executes at every Python startup{note}: {executable_lines[0][:120]}",
                )
            )

    return findings


# ---------------------------------------------------------------------------
# Check: known host-level persistence
# ---------------------------------------------------------------------------


def check_host() -> list[Finding]:
    """Look for known host-level persistence under the current user's home.

    Deliberately independent of the PATH argument: host artifacts are global,
    so `audit_workspace.py ./some-repo` still reports them.
    """
    findings: list[Finding] = []
    for raw in KEYV_HOST_ARTIFACTS:
        path = Path(os.path.expanduser(raw))
        if path.exists():
            findings.append(
                Finding(
                    "host",
                    SEVERITY_HIGH,
                    str(path),
                    "keyv-worm token-revocation watcher artifact; REMOVE THIS BEFORE ROTATING ANY CREDENTIAL",
                )
            )
    return findings


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def format_report(findings: list[Finding], target: Path, checks: list[str]) -> str:
    lines: list[str] = []
    lines.append(f"audit_workspace: {target}")
    lines.append(f"checks: {', '.join(checks)}")
    lines.append("")

    if not findings:
        lines.append("No findings.")
        return "\n".join(lines)

    high = [f for f in findings if f.severity == SEVERITY_HIGH]
    info = [f for f in findings if f.severity == SEVERITY_INFO]

    for group, label in ((high, SEVERITY_HIGH), (info, SEVERITY_INFO)):
        if not group:
            continue
        lines.append(f"[{label}] {len(group)} finding(s)")
        for f in group:
            lines.append(f"  ({f.check}) {f.path}")
            lines.append(f"      {f.detail}")
        lines.append("")

    if any(f.check == "host" for f in high):
        lines.append(
            "WARNING: host persistence found. The keyv worm's watcher evaluates an "
            "operator-supplied handler when a stolen token stops working, so revoking "
            "credentials first is the trigger. Isolate the machine, remove the watcher, "
            "then rotate from a different clean machine."
        )
        lines.append("")

    lines.append(
        "Next: guidelines/hardening-agent-workspaces.md -> 'If You Have Hits'. "
        "Findings are read-only; nothing was modified."
    )
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="audit_workspace.py",
        description=(
            "Audit a repository and host for open-time and load-time supply-chain "
            "persistence (agent/editor autostart config, hidden Unicode in agent "
            "instructions, .pth interpreter hooks, known host persistence)."
        ),
        epilog=(
            "Exit codes: 0 clean, 1 informational findings, 2 error, 3 HIGH findings.\n"
            "Read-only: never edits, deletes, or executes anything it finds.\n"
            "The host check inspects the current user's home directory and is\n"
            "independent of PATH; scanning ./some-repo still reports host persistence."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="repository or directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--only",
        choices=("autostart", "unicode", "pth", "host"),
        action="append",
        help="run only the named check (repeatable); default runs all four",
    )
    parser.add_argument(
        "--scan-site-packages",
        action="store_true",
        help="also scan the active interpreter's site-packages for .pth hooks",
    )
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    return parser


def main(argv: list[str]) -> int:
    args = build_arg_parser().parse_args(argv)

    target = Path(args.path).expanduser()
    if not target.is_dir():
        print(f"error: not a directory: {target}", file=sys.stderr)
        return 2
    target = target.resolve()

    checks = args.only or ["autostart", "unicode", "pth", "host"]

    findings: list[Finding] = []
    if "autostart" in checks:
        findings.extend(check_autostart(target))
    if "unicode" in checks:
        findings.extend(check_unicode(target))
    if "pth" in checks:
        findings.extend(check_pth(target, args.scan_site_packages))
    if "host" in checks:
        findings.extend(check_host())

    if args.json:
        print(
            json.dumps(
                {
                    "target": str(target),
                    "checks": checks,
                    "findings": [f.__dict__ for f in findings],
                },
                indent=2,
            )
        )
    else:
        print(format_report(findings, target, checks))

    if any(f.severity == SEVERITY_HIGH for f in findings):
        return 3
    if findings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
