#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
#
# validate-docs.py
#
# Lint pass for the markdown corpus of this repo. Today it checks one thing:
# every package-manager environment-variable name that appears in the docs is
# either in tests/known-env-vars.txt or matches a documented escape hatch.
#
# Why this exists: UV_ONLY_BINARY shipped in the docs for months before review
# caught it as a non-existent uv env var. An allow-list catches that whole
# class of bug without requiring brittle live fetches against upstream docs.
#
# Run locally:
#     uv run tests/validate-docs.py
#     # or: python3 tests/validate-docs.py
#
# Exit codes:
#     0  all checks passed
#     1  one or more violations found (printed to stderr)
#     2  setup error (missing allow-list, etc.)

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ALLOW_LIST = REPO_ROOT / "tests" / "known-env-vars.txt"

# Files to scan. The supply-chain-hardening-engineering-review.md is
# intentionally NOT scanned: it contains historical references to incorrect
# env vars by design.
SCAN_GLOBS = [
    "README.md",
    "AGENTS.md",
    "SUPPLY-CHAIN-SECURITY.md",
    "guidelines/*.md",
    "research/*.md",
]

# Match tokens that look like package-manager env vars.
# Conservative: only match the prefixes we expect to see in this repo, so a
# random ALL_CAPS variable in prose text does not get flagged.
ENV_VAR_PATTERN = re.compile(
    r"\b("
    r"NPM_CONFIG_[A-Z0-9_]+"
    r"|PNPM_CONFIG_[A-Z0-9_]+"
    r"|PIP_[A-Z0-9_]+"
    r"|UV_[A-Z0-9_]+"
    r"|CARGO_[A-Z0-9_]+"
    r"|GOPROXY|GOSUMDB|GONOSUMDB|GONOSUMCHECK|GOPRIVATE|GOFLAGS|GOTOOLCHAIN|GOMODCACHE"
    r"|GOVULNCHECK_VERSION"
    r")\b"
)

# Stale-policy and rendering checks. These catch two regression classes found in
# PR review:
#  1. Old 7-day cool-off values that survive a "14 days" prose edit (the repo-wide
#     default is 14 days; see README "The Default Policy"). We match concrete config
#     tokens only, NOT bare "7 days" prose, so the README's intentional 7-vs-14
#     rationale ("a 7-day window misses it", "3-7 days") is allowed.
#  2. A comparison like ">= 11.5.1" that a Markdown formatter wrapped onto its own
#     line, turning it into an accidental blockquote ("  > = 11.5.1").
POLICY_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b10080\b"), "stale 7-day value 10080 (use 20160 = 14 days)"),
    (re.compile(r"\bP7D\b"), "stale 7-day ISO duration P7D (use P14D)"),
    (re.compile(r"-v-7d\b"), "stale 7-day date offset -v-7d (use -v-14d)"),
    (re.compile(r"7 days ago"), "stale '7 days ago' date offset (use '14 days ago')"),
    (re.compile(r"MIN(?:IMUM)?_RELEASE_AGE\s*[:=]\s*7\b"), "stale MIN_RELEASE_AGE=7 (use 14)"),
    (re.compile(r"min-release-age[ =]+7\b"), "stale min-release-age 7 (use 14)"),
    (re.compile(r'EXCLUDE_NEWER["\s:=]+7 days'), "stale EXCLUDE_NEWER \"7 days\" (use \"14 days\")"),
    (re.compile(r"^\s*>\s*="), "blockquote-wrapped comparison (rewrite 'X+' instead of '>= X')"),
]


def find_policy_violations(path: Path) -> list[tuple[int, str]]:
    violations: list[tuple[int, str]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for pattern, message in POLICY_PATTERNS:
            if pattern.search(line):
                violations.append((lineno, message))
    return violations

# Explicit allow-list of names that show up in docs but are NOT canonical
# package-manager env vars (e.g. ad-hoc shell-script intermediaries).
PROSE_EXEMPT = {
    "NPM_HARDENING_BEFORE",   # internal shell var in the npm hardening script
}


def load_allow_list() -> set[str]:
    if not ALLOW_LIST.is_file():
        print(f"setup error: {ALLOW_LIST} not found", file=sys.stderr)
        sys.exit(2)
    allowed: set[str] = set()
    for raw in ALLOW_LIST.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            allowed.add(line)
    return allowed


def iter_doc_paths() -> list[Path]:
    out: list[Path] = []
    for pattern in SCAN_GLOBS:
        for path in sorted(REPO_ROOT.glob(pattern)):
            if path.is_file():
                out.append(path)
    return out


def find_violations(path: Path, allowed: set[str]) -> list[tuple[int, str]]:
    violations: list[tuple[int, str]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for match in ENV_VAR_PATTERN.finditer(line):
            name = match.group(1)
            if name in allowed or name in PROSE_EXEMPT:
                continue
            violations.append((lineno, name))
    return violations


def main() -> int:
    allowed = load_allow_list()
    seen_unknown: dict[str, list[tuple[Path, int]]] = {}
    policy_hits: list[tuple[Path, int, str]] = []
    for path in iter_doc_paths():
        for lineno, name in find_violations(path, allowed):
            seen_unknown.setdefault(name, []).append((path, lineno))
        for lineno, message in find_policy_violations(path):
            policy_hits.append((path, lineno, message))

    if not seen_unknown and not policy_hits:
        print(f"validate-docs.py: OK ({len(allowed)} known env vars, all docs clean)")
        return 0

    print("validate-docs.py: FAIL", file=sys.stderr)
    if seen_unknown:
        print(
            "The following env-var-shaped tokens appear in the docs but are not in "
            f"{ALLOW_LIST.relative_to(REPO_ROOT)}:",
            file=sys.stderr,
        )
        for name, hits in sorted(seen_unknown.items()):
            print(f"  {name}:", file=sys.stderr)
            for path, lineno in hits:
                print(f"    {path.relative_to(REPO_ROOT)}:{lineno}", file=sys.stderr)
        print(
            "\nFix by either: (a) confirming the name is correct and adding it to "
            f"{ALLOW_LIST.relative_to(REPO_ROOT)}, or (b) correcting the docs.",
            file=sys.stderr,
        )
    if policy_hits:
        print("\nStale-policy / rendering issues:", file=sys.stderr)
        for path, lineno, message in policy_hits:
            print(f"  {path.relative_to(REPO_ROOT)}:{lineno}: {message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
