---
type: is
id: is-01krerf45aqyaawjqn27613k8q
title: Verify PyPI Part 1 background claims
kind: task
status: closed
priority: 1
version: 3
labels:
  - validation
  - pypi
dependencies: []
created_at: 2026-05-12T18:51:24.201Z
updated_at: 2026-05-12T18:55:59.531Z
closed_at: 2026-05-12T18:55:59.530Z
close_reason: "Verified Part 1 background: setup.py/sdist arbitrary code execution confirmed, wheel bypass confirmed, dependency confusion mechanism (torchtriton) confirmed, pip precedence chain (CLI > env > config > defaults) confirmed. Minor note: doc mentions pyproject.toml [tool.pip] as project-local config but that is still a feature request (pypa/pip#13003); the broader claim that env vars beat config files is correct via site/user/global .conf. No fix needed."
---
Fact-check Part 1 of research-pypi-supply-chain-hardening.md: PyPI threat model, install-script differences from npm (setup.py + PEP 517 build backends), wheel vs sdist surface, dependency confusion. Cross-reference current PyPA, Snyk, Sonatype writeups.
