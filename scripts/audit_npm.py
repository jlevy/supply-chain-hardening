#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
#
# audit-npm.py
#
# Audit installed npm packages against the OSV vulnerability database.
#
# Default target is the global node_modules ($(npm root -g)). The primary use
# case: after `npm install -g <pkg>`, verify nothing in the transitive
# dependency tree matches a known malicious-version advisory.
#
# This script is deliberately written in Python (stdlib only) rather than
# Node.js so the audit tool does not ride on the same supply chain it audits.
#
# Run with one of:
#     uv run scripts/audit-npm.py [args...]     # preferred: hermetic Python
#     python3 scripts/audit-npm.py [args...]    # fallback: system Python
#
# Zero third-party dependencies. PEP 723 inline metadata above declares this
# explicitly; uv enforces it.
#
# Documentation: ./README.md
# Upstream API:  https://google.github.io/osv.dev/api/
#
# Exit codes:
#     0  no OSV-matched vulnerabilities found
#     1  one or more ordinary CVE advisories found (no MAL-* IDs)
#     2  error (network failure, invalid arguments, missing target)
#     3  one or more malicious-package advisories found (MAL-* ID)
#
# Exit 3 is reserved for the strictest signal: OSV's dedicated malicious-package
# corpus matched something installed. CI jobs should typically fail-loud on 3 and
# may want to treat 1 differently from 3 in alerting.

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

OSV_BATCH_URL = "https://api.osv.dev/v1/querybatch"
OSV_VULN_URL = "https://api.osv.dev/v1/vulns"
BATCH_SIZE = 1000  # OSV /querybatch supports large batches; 1000 is conservative
FETCH_TIMEOUT_SECONDS = 30
HTTP_RETRY_ATTEMPTS = 4         # initial try plus 3 retries
HTTP_RETRY_INITIAL_DELAY = 1.0  # seconds; doubles per retry (1s, 2s, 4s)
RETRYABLE_HTTP_STATUSES = frozenset({408, 429, 500, 502, 503, 504})


# ---------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Package:
    """A single installed package@version pair."""
    name: str
    version: str
    path: str | None = None  # filesystem path; None for --packages input


@dataclass
class Hit:
    """A scanned package whose version matches one or more OSV advisories."""
    name: str
    version: str
    vulns: list[dict[str, Any]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Package discovery
# ---------------------------------------------------------------------------

def resolve_global_node_modules() -> Path:
    """Return the path reported by `npm root -g`."""
    result = subprocess.run(
        ["npm", "root", "-g"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def walk_node_modules(root: Path) -> list[Package]:
    """
    Walk a node_modules tree breadth-first and collect (name, version) from
    every package.json. Handles scoped packages and nested node_modules.
    Malformed package.json files are silently skipped.
    """
    found: list[Package] = []
    stack: list[Path] = [root]
    while stack:
        directory = stack.pop()
        try:
            entries = list(directory.iterdir())
        except OSError:
            continue
        for entry in entries:
            if not entry.is_dir():
                continue
            # Scoped namespace directory: recurse one level to find packages.
            if entry.name.startswith("@"):
                stack.append(entry)
                continue
            pkg_json = entry / "package.json"
            if pkg_json.is_file():
                pkg = read_package_json(pkg_json)
                if pkg is not None:
                    found.append(Package(pkg["name"], pkg["version"], str(entry)))
            nested = entry / "node_modules"
            if nested.is_dir():
                stack.append(nested)
    return found


def read_package_json(path: Path) -> dict[str, str] | None:
    """Return {name, version} if both fields are non-empty strings, else None."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    name = data.get("name")
    version = data.get("version")
    if isinstance(name, str) and isinstance(version, str) and name and version:
        return {"name": name, "version": version}
    return None


def parse_package_specs(specs: list[str]) -> list[Package]:
    """
    Parse "pkg@ver" or "@scope/pkg@ver" strings into Package objects. The
    separator is the LAST '@' so scoped names parse correctly.
    """
    out: list[Package] = []
    for spec in specs:
        at = spec.rfind("@")
        if at <= 0:
            raise ValueError(f"Invalid package spec (expected pkg@ver): {spec}")
        out.append(Package(spec[:at], spec[at + 1:]))
    return out


def dedupe_packages(packages: list[Package]) -> list[Package]:
    """Drop duplicate (name, version) pairs while preserving order."""
    seen: set[tuple[str, str]] = set()
    out: list[Package] = []
    for p in packages:
        key = (p.name, p.version)
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out


# ---------------------------------------------------------------------------
# OSV queries
# ---------------------------------------------------------------------------

def _request_with_retry(request: urllib.request.Request) -> dict[str, Any]:
    """
    Issue an HTTP request with bounded exponential backoff on transient failures.
    Retries on 408/429/5xx HTTP statuses and on URLError. Other 4xx are returned
    immediately by raising.
    """
    delay = HTTP_RETRY_INITIAL_DELAY
    last_err: Exception | None = None
    for attempt in range(HTTP_RETRY_ATTEMPTS):
        try:
            with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            last_err = err
            if err.code not in RETRYABLE_HTTP_STATUSES:
                raise
        except urllib.error.URLError as err:
            last_err = err
        if attempt < HTTP_RETRY_ATTEMPTS - 1:
            time.sleep(delay)
            delay *= 2
    assert last_err is not None
    raise last_err


def http_post_json(url: str, body: dict[str, Any]) -> dict[str, Any]:
    """POST a JSON body and return the parsed JSON response. Retries on transient errors."""
    payload = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"content-type": "application/json"},
        method="POST",
    )
    return _request_with_retry(request)


def http_get_json(url: str) -> dict[str, Any]:
    """GET a JSON resource and return the parsed JSON response. Retries on transient errors."""
    request = urllib.request.Request(url, method="GET")
    return _request_with_retry(request)


def batch_query_osv(packages: list[Package]) -> list[list[str]]:
    """
    Submit packages to OSV /v1/querybatch in chunks of BATCH_SIZE. Returns a
    list aligned to the input order; each element is the list of OSV
    vulnerability IDs for that package (empty list if no matches).
    """
    ids_by_query: list[list[str]] = []
    for start in range(0, len(packages), BATCH_SIZE):
        chunk = packages[start:start + BATCH_SIZE]
        body = {
            "queries": [
                {
                    "package": {"name": p.name, "ecosystem": "npm"},
                    "version": p.version,
                }
                for p in chunk
            ]
        }
        data = http_post_json(OSV_BATCH_URL, body)
        for result in data.get("results", []):
            ids_by_query.append([v["id"] for v in result.get("vulns", [])])
    return ids_by_query


def fetch_vuln_details(ids: list[str]) -> dict[str, dict[str, Any]]:
    """Fetch full advisory data for each OSV ID. Failures recorded inline."""
    details: dict[str, dict[str, Any]] = {}
    for vid in ids:
        try:
            details[vid] = http_get_json(f"{OSV_VULN_URL}/{vid}")
        except (urllib.error.URLError, json.JSONDecodeError) as err:
            details[vid] = {"id": vid, "error": str(err)}
    return details


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def is_malicious(vuln: dict[str, Any]) -> bool:
    """
    Return True only for advisories from OSV's dedicated malicious-package
    corpus (IDs prefixed `MAL-`).

    Pitfall: do not broaden this to a summary-text check ('malicious' substring
    or similar). CVE summaries legitimately describe malicious actors as part
    of the threat model (e.g. "denial of service via a malicious FTP server"
    or "Malicious WebSocket length overflow"), and matching on those produces
    high-confidence-looking false positives. If a malicious-package advisory
    is filed under a non-MAL ID (rare — usually a GHSA cross-reference), it
    will still be reported as a normal vulnerability hit but without the
    elevated "[MALICIOUS]" tag.
    """
    return vuln.get("id", "").startswith("MAL-")


def advisory_affects_version(vuln: dict[str, Any], name: str, version: str) -> bool:
    """
    Verify that an OSV advisory actually applies to (name, version).

    Why this exists: OSV's /v1/querybatch endpoint can over-match when an
    advisory has both an explicit `versions` list and a permissive `ranges`
    SEMVER (e.g. {events: [{introduced: 0}]} with no `fixed` event). The
    `versions` list, when present, is the canonical narrow set of affected
    versions and should take precedence.

    Returns True when:
      - No matching affected-package entry has an explicit `versions` list
        (trust OSV's batch match), OR
      - A `versions` list IS present and the queried version is in it.

    Returns False only when an explicit `versions` list exists and the
    queried version is not in it.
    """
    has_versions_list = False
    for affected in vuln.get("affected", []):
        pkg = affected.get("package") or {}
        if pkg.get("name") != name or pkg.get("ecosystem") != "npm":
            continue
        versions = affected.get("versions")
        if versions is None:
            continue
        has_versions_list = True
        if version in versions:
            return True
    # If no affected entry had an explicit versions list, trust the batch match.
    return not has_versions_list


def severity_of(vuln: dict[str, Any]) -> str:
    severity = vuln.get("severity") or []
    if severity and isinstance(severity, list) and severity[0].get("score"):
        return severity[0]["score"]
    return (vuln.get("database_specific") or {}).get("severity") or "unspecified"


def format_text_report(hits: list[Hit], scanned: int, target: str) -> str:
    lines: list[str] = []
    lines.append(f"Scanned {scanned} unique package@version pair(s) from {target}.")
    lines.append("")
    if not hits:
        lines.append("OK: no OSV-known vulnerabilities found.")
        return "\n".join(lines)

    malicious_count = sum(1 for h in hits if any(is_malicious(v) for v in h.vulns))
    if malicious_count:
        lines.append(
            f"ALERT: {malicious_count} package(s) match malicious-package advisories."
        )
    lines.append(f"Found {len(hits)} package version(s) with OSV-known issues:")
    lines.append("")
    for hit in hits:
        marker = "MALICIOUS" if any(is_malicious(v) for v in hit.vulns) else "advisory"
        lines.append(f"[{marker}] {hit.name}@{hit.version}")
        for v in hit.vulns:
            lines.append(f"    - {v.get('id')}: {v.get('summary') or '(no summary)'}")
            lines.append(f"      severity: {severity_of(v)}")
            refs = v.get("references") or []
            if refs and refs[0].get("url"):
                lines.append(f"      ref: {refs[0]['url']}")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="audit-npm.py",
        description=(
            "Audit installed npm packages against the OSV vulnerability database. "
            "Default target is the global node_modules ($(npm root -g))."
        ),
        epilog=(
            "Examples:\n"
            "  uv run scripts/audit-npm.py\n"
            "  uv run scripts/audit-npm.py --node-modules ./node_modules\n"
            "  uv run scripts/audit-npm.py --packages chalk@5.6.1 debug@4.4.2\n"
            "  uv run scripts/audit-npm.py --json > audit.json\n\n"
            "Exit codes: 0 clean, 1 CVE hits, 2 error, 3 malicious-package hits."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    target = parser.add_mutually_exclusive_group()
    target.add_argument(
        "--global",
        dest="use_global",
        action="store_true",
        help="Scan the global node_modules ($(npm root -g)). This is the default.",
    )
    target.add_argument(
        "--node-modules",
        metavar="PATH",
        help="Scan a specific node_modules directory.",
    )
    target.add_argument(
        "--packages",
        nargs="+",
        metavar="PKG@VER",
        help="Check specific package@version pairs (no directory scan).",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit machine-readable JSON instead of text.",
    )
    return parser


def main(argv: list[str]) -> int:
    args = build_arg_parser().parse_args(argv)

    # Build the package list and a human-readable description of the source.
    try:
        if args.packages:
            packages = parse_package_specs(args.packages)
            target_description = f"--packages ({len(packages)} input)"
        else:
            root = (
                Path(args.node_modules).resolve()
                if args.node_modules
                else resolve_global_node_modules()
            )
            if not root.is_dir():
                print(f"node_modules not found: {root}", file=sys.stderr)
                return 2
            packages = walk_node_modules(root)
            target_description = str(root)
    except (ValueError, subprocess.CalledProcessError, FileNotFoundError) as err:
        print(f"Input error: {err}", file=sys.stderr)
        return 2

    packages = dedupe_packages(packages)

    if not args.as_json:
        print(
            f"Scanning {len(packages)} unique package(s) against OSV...",
            file=sys.stderr,
        )

    try:
        ids_by_query = batch_query_osv(packages)
    except (urllib.error.URLError, json.JSONDecodeError) as err:
        print(f"OSV /querybatch failed: {err}", file=sys.stderr)
        return 2

    all_ids: list[str] = []
    seen_ids: set[str] = set()
    for ids in ids_by_query:
        for vid in ids:
            if vid not in seen_ids:
                seen_ids.add(vid)
                all_ids.append(vid)

    details: dict[str, dict[str, Any]] = {}
    if all_ids:
        if not args.as_json:
            print(
                f"Fetching details for {len(all_ids)} OSV advisorie(s)...",
                file=sys.stderr,
            )
        details = fetch_vuln_details(all_ids)

    hits: list[Hit] = []
    for pkg, ids in zip(packages, ids_by_query):
        if not ids:
            continue
        kept_vulns: list[dict[str, Any]] = []
        for vid in ids:
            vuln = details.get(vid, {"id": vid})
            # If detail fetch failed, keep the bare ID rather than silently
            # dropping. Otherwise, only keep matches that genuinely apply to
            # the installed version (filters out OSV advisories with overly
            # broad SEMVER ranges that contradict their own `versions` list).
            if "error" in vuln or advisory_affects_version(vuln, pkg.name, pkg.version):
                kept_vulns.append(vuln)
        if kept_vulns:
            hits.append(Hit(name=pkg.name, version=pkg.version, vulns=kept_vulns))

    if args.as_json:
        json.dump(
            {
                "scanned": len(packages),
                "target": target_description,
                "hits": [
                    {"name": h.name, "version": h.version, "vulns": h.vulns}
                    for h in hits
                ],
            },
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        print(format_text_report(hits, len(packages), target_description))

    if not hits:
        return 0
    has_malicious = any(any(is_malicious(v) for v in h.vulns) for h in hits)
    return 3 if has_malicious else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
