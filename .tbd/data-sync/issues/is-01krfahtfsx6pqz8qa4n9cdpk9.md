---
type: is
id: is-01krfahtfsx6pqz8qa4n9cdpk9
title: Tighten unbounded language (defeats nearly all, neutralises) in README and portable doc
kind: task
status: closed
priority: 2
version: 3
labels:
  - docs
  - language
dependencies: []
parent_id: is-01krfaben9ca381zwmq8ejcsge
created_at: 2026-05-13T00:07:26.969Z
updated_at: 2026-05-13T01:29:06.269Z
closed_at: 2026-05-13T01:29:06.268Z
close_reason: "Replaced 'defeats nearly every named incident' / 'neutralises nearly all of it' in README and SUPPLY-CHAIN-SECURITY.md with bounded language: 'neutralises the dominant fast-yanked-incident pattern.' Added explicit list of attack classes the cool-off does not neutralise: long-lived typosquats (BoltDB ~3 years; ctx ~10 days), pre-captured lockfile entries, runtime payloads on import/build."
---
# Tighten unbounded language ("defeats nearly all of it", etc.)

## Problem

README.md and SUPPLY-CHAIN-SECURITY.md include statements like:

- SUPPLY-CHAIN-SECURITY.md: "Most malicious versions are detected and yanked
  within hours; a one-week cooldown defeats nearly every named incident in
  the 2025-2026 wave."
- SUPPLY-CHAIN-SECURITY.md: "A 7-day install cooldown plus disabled install
  scripts neutralises nearly all of it."
- README.md: "A 7-day rolling install quarantine plus disabled install-time
  scripts defeats most of them."

Reviewer correctly notes these are unbounded claims. Some attacks have
longer dwell times (BoltDB cached ~3 years; ctx ~10 days; faster_log
unspecified). And "defeats" overstates - it prevents installation during
the live window, but a lockfile that already captured the bad version
is not "defeated" by a future quarantine.

## Fix

Bound the language to what is actually true:

- Change "defeats nearly every" / "defeats nearly all" to: "neutralises
  the dominant pattern: fast-yanked named incidents (qix, Shai-Hulud,
  Axios, TanStack, Ultralytics, LiteLLM, Mini Shai-Hulud, etc.) where
  malicious versions lived for minutes to hours before being yanked."
- Add an explicit caveat that longer-lived compromises (BoltDB-style
  proxy-cached typosquats, expired-domain account takeovers like ctx)
  require additional controls: lockfile review, typo-resistance checks,
  account-recovery hygiene.
- Where the doc states "blocks setup.py code execution" or similar,
  ensure it is correctly bounded to sdists; wheels can still execute
  malicious code on import (which is documented elsewhere but worth a
  reminder in the short doc).

## Files to edit

- README.md
- SUPPLY-CHAIN-SECURITY.md
- AGENTS.md (verify it does not repeat the same hyperbole)

## Acceptance

- No "defeats nearly all"/"nearly every" phrasing without a bounded
  qualifier.
- The doc names the class of attack the cool-off does not catch
  (long-lived typosquats, lockfile capture, runtime wheel payloads).
