# Compromised Packages

**Last updated:** 2026-08-06

**Author:** Joshua Levy (github.com/jlevy) with agent assistance

A cross-ecosystem reference table of named supply-chain attacks on open-source package
registries. Scope: malicious-package incidents only (maintainer takeover, worm
propagation, deliberate malicious publish, GitHub Actions exploitation), not regular
CVEs in otherwise-legitimate packages.

This is a living document.
Per-ecosystem hardening guides reference this table rather than duplicating it.
Update procedure is in [self-update-instructions.md](self-update-instructions.md) →
“Updating `compromised-packages.md`”.

## Scope

This is a **curated watch list, not an exhaustive feed.** Notable incidents that
defenders should recognise by name; high download counts, novel mechanisms, named
campaigns, or persistence patterns.
For comprehensive cross-ecosystem coverage, use the systems of record (OSV.dev, GHSA,
RustSec, PyPA Advisory DB, Go Vulnerability DB) listed in
[README.md → “Authoritative Sources”](README.md#authoritative-sources).

**Included:** confirmed malicious publishes, multi-source verified per
[self-update-instructions.md](self-update-instructions.md) → “Updating
`compromised-packages.md`”.

**Excluded:** regular CVEs in legitimate packages (DoS, ReDoS, prototype pollution,
etc.). Typosquats preempted before any download.
Unverified rumours and single-source claims.
Routine low-impact typosquats with negligible download counts.

**Cross-ecosystem propagation:** if a single campaign hit packages in multiple
ecosystems, each ecosystem gets its own row so per-ecosystem audits stay
straightforward.

**Aging:** the Active Watch List is capped.
A row moves to [Historical Incidents](#historical-incidents-recognition-only) once it is
more than about twelve months old and its artifacts are no longer served (versions
yanked, no proxy cache still delivering the payload).
The pattern keeps its recognition value there; the per-version IOCs live on in the
systems of record, which cover old incidents completely.
This cap is what keeps the file a watch list rather than a slowly-growing feed.

## Active Watch List (Actionable IOCs)

Incidents from roughly the last twelve months, plus any older incident whose artifacts
are still being served (Go module-proxy caching keeps some payloads fetchable long after
the source repository is gone).
Every row has either an exact `pkg@version` IOC, a complete affected-package list at the
linked URL, or a canonical GHSA / RUSTSEC ID that resolves to one.
Defenders running a scan can use this table directly without follow-up research.

| Date | Name | Ecosystem | Scale | Affected `pkg@version` (representative; full list at the linked source) | Vector | References |
| --- | --- | --- | --- | --- | --- | --- |
| 2025-08 | Nx packages | npm | ~10 packages | `nx@21.5.0`-`21.5.3`, `@nx/devkit@21.5.0`-`21.5.3`, `@nx/enterprise-cloud@3.2.0`, `@nx/eslint@21.5.0`, `@nx/js@21.5.0`/`21.5.1`, `@nx/key@3.2.0`, `@nx/node@21.5.0`, `@nx/workspace@21.5.0` | Maintainer-account compromise; stole npm and GitHub tokens | OSV; Snyk |
| 2025-09-08 | “qix” maintainer phish | npm | 18+ packages, ~billions of weekly downloads combined, malicious versions live ~2 hours | `ansi-styles@6.2.2`, `debug@4.4.2`, `chalk@5.6.1`, `supports-color@10.2.1`, `strip-ansi@7.1.1`, `ansi-regex@6.2.1`, `wrap-ansi@9.0.1`, `color-convert@3.1.1`, `color-name@2.0.1`, `is-arrayish@0.3.3`, `slice-ansi@7.1.1`, `error-ex@1.3.3`, `simple-swizzle@0.2.3`, `supports-hyperlinks@4.1.1`, `chalk-template@1.1.1`, `backslash@0.2.1`, `color-string@2.1.1`, `has-ansi@6.0.1`, `proto-tinker-wc@0.1.87` | Phishing via fake `npmjs.help` 2FA-reset email; collected user/pass/TOTP | OSV (`MAL-2025-46969`, `MAL-2025-46974`); [Socket](https://socket.dev/blog/npm-author-qix-compromised-in-major-supply-chain-attack); [StepSecurity](https://www.stepsecurity.io/blog/20-popular-npm-packages-compromised-chalk-debug-strip-ansi-color-convert-wrap-ansi) |
| 2025-09 | faster_log / async_println crypto-key theft | crates.io | 2 crates, ~8,424 combined downloads | `faster_log` (all versions by `rustguruman`), `async_println` (all versions by `dumbnbased`) | Typosquat of `fast_log`; runtime exfil of Solana/Ethereum private keys via Cloudflare Workers | [Rust Blog](https://blog.rust-lang.org/2025/09/24/crates.io-malicious-crates-fasterlog-and-asyncprintln/); [Socket](https://socket.dev/blog/two-malicious-rust-crates-impersonate-popular-logger-to-steal-wallet-keys); [The Hacker News](https://thehackernews.com/2025/09/malicious-rust-crates-steal-solana-and.html) |
| 2025-09-15 | Shai-Hulud 1.0 worm | npm | 500+ packages, ~180 confirmed | `@ctrl/tinycolor@4.1.1`, `@ctrl/tinycolor@4.1.2` (initial vector), `ngx-bootstrap`, `ng2-file-upload`, `angulartics2`, many `@ctrl/*` | Self-replicating worm; stolen tokens auto-republished to other packages owned by victim | [Sysdig](https://www.sysdig.com/blog/shai-hulud-the-novel-self-replicating-worm-infecting-hundreds-of-npm-packages); [CISA](https://www.cisa.gov/news-events/cybersecurity-advisories/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem); [Unit 42](https://unit42.paloaltonetworks.com/npm-supply-chain-attack/) |
| 2025-11-24 | Shai-Hulud 2.0 | npm | 796 packages, ~25K repos, ~350 maintainers | Full IOC list: `https://blog.ehsan.it/shai-hulud-v2-ioc.json` | Worm plus `preinstall` script invoking `setup_bun.js` / `bun_environment.js`; registers self-hosted GitHub runner named `SHA1HULUD` for persistence | [Datadog Security Labs](https://securitylabs.datadoghq.com/articles/shai-hulud-2.0-npm-worm/); [Wiz](https://www.wiz.io/blog/shai-hulud-2-0-ongoing-supply-chain-attack); [Netskope](https://www.netskope.com/blog/shai-hulud-2-0-aggressive-automated-one-of-fastest-spreading-npm-supply-chain-attacks-ever-observed) |
| 2025-12 | evm-units / uniswap-utils Web3 targeting | crates.io | 2 crates, ~14,400 combined downloads | `evm-units` (all versions by `ablerust`), `uniswap-utils` (14 versions) | Transitive-dep facade; OS-specific binary download and execution via `#[ctor::ctor]` | [Rust Blog](https://blog.rust-lang.org/2025/12/03/crates.io-malicious-crates-evm-units-and-uniswap-utils/); [Socket](https://socket.dev/blog/malicious-rust-crate-evm-units-serves-cross-platform-payloads); [The Hacker News](https://thehackernews.com/2025/12/malicious-rust-crate-delivers-os.html) |
| 2025-12 | finch-rst / sha-rst credential theft | crates.io | 3 crates, ~61 combined downloads | `finch-rst`, `sha-rst`, `finch_cli_rust` | Typosquat of `finch`/`finch_cli`; credential exfiltration payload in `sha-rst` | [RUSTSEC-2025-0150](https://rustsec.org/advisories/RUSTSEC-2025-0150.html); [RUSTSEC-2025-0151](https://rustsec.org/advisories/RUSTSEC-2025-0151.html); [RUSTSEC-2025-0152](https://rustsec.org/advisories/RUSTSEC-2025-0152.html) |
| 2026-02..03 | Time-utility .env exfiltration campaign | crates.io | 5 crates | `chrono_anchor`, `dnp3times`, `time_calibrator`, `time_calibrators`, `time-sync` | Impersonation of time utilities; `.env` exfiltration; `chrono_anchor` obfuscated | [Socket](https://socket.dev/blog/5-malicious-rust-crates-posed-as-time-utilities-to-exfiltrate-env-files); [The Hacker News](https://thehackernews.com/2026/03/five-malicious-rust-crates-and-ai-bot.html) |
| 2026-03-20..04-08 | CanisterWorm / CanisterSprawl (post-Trivy) | npm | 141 malicious versions across 66+ packages; CanisterSprawl wave ~8,424 weekly downloads combined | `@automagik/genie@4.260421.33`-`@automagik/genie@4.260421.39`, `pgserve@1.1.11`, `pgserve@1.1.12`, `pgserve@1.1.13` (CanisterSprawl); 47+ packages incl `@opengov/*` (initial CanisterWorm wave) | npm fallout of the Aqua Trivy GitHub Action compromise (same root cause as the LiteLLM row below); self-replicating worm whose `deploy.js` harvests npm tokens and republishes, using a decentralized (IPFS/ICP-canister) C2 for resilience; TeamPCP | [The Hacker News](https://thehackernews.com/2026/03/trivy-supply-chain-attack-triggers-self.html); [Aikido](https://www.aikido.dev/blog/teampcp-deploys-worm-npm-trivy-compromise); [Mend](https://www.mend.io/blog/canisterworm-the-self-spreading-npm-attack-that-uses-a-decentralized-server-to-stay-alive/); [Socket](https://socket.dev/blog/namastex-npm-packages-compromised-canisterworm) |
| 2026-03-24 | LiteLLM / TeamPCP | PyPI | 2 versions, ~119K downloads in ~40 minutes; ~95M monthly downloads | `litellm@1.82.7`, `litellm@1.82.8` | Stolen PyPI token via compromised Trivy GitHub Action in CI/CD; credential harvesting and systemd backdoor; TeamPCP | [PyPI incident report](https://blog.pypi.org/posts/2026-04-02-incident-report-litellm-telnyx-supply-chain-attack/); [Datadog Security Labs](https://securitylabs.datadoghq.com/articles/litellm-compromised-pypi-teampcp-supply-chain-campaign/); [Snyk](https://snyk.io/blog/poisoned-security-scanner-backdooring-litellm/); GHSA-5mg7-485q-xm76 |
| 2026-03-31 | Axios | npm | 2 versions, ~70M weekly downloads | `axios@1.14.1`, `axios@0.30.4` | Sapphire Sleet (DPRK); pulls 2nd-stage RAT | [CISA](https://www.cisa.gov/news-events/cybersecurity-advisories/2026/04/20/supply-chain-compromise-impacts-axios-node-package-manager); [Microsoft Security](https://www.microsoft.com/en-us/security/blog/2026/04/01/mitigating-the-axios-npm-supply-chain-compromise/); [Mandiant](https://cloud.google.com/blog/topics/threat-intelligence/north-korea-threat-actor-targets-axios-npm-package) |
| 2026-04 | mysten-metrics build.rs exfiltration | crates.io | 1 crate | `mysten-metrics@9.0.3` | Malicious `build.rs` runs `env`/`cat`/`ls -R` at compile time, exfils via HTTP POST | [GHSA-G38R-8GMR-GHRF](https://github.com/advisories/GHSA-G38R-8GMR-GHRF); RUSTSEC-2026-0107 |
| 2026-04-22 | `@bitwarden/cli` (TeamPCP / Checkmarx) | npm | 1 version, live ~17:57-19:30 ET (~93 min), ~334 downloads | `@bitwarden/cli@2026.4.0` (clean: `2026.4.1`; last clean before: `2026.3.0`) | Malicious build published through the npm delivery path during the Checkmarx supply-chain incident; `bw1.js` harvests GitHub/npm tokens, `.ssh`, `.env`, shell history, and cloud secrets, exfiltrates to private domains and GitHub commits, and self-propagates by backdooring packages the victim can publish | [Bitwarden statement](https://community.bitwarden.com/t/bitwarden-statement-on-checkmarx-supply-chain-incident/96127); [The Hacker News](https://thehackernews.com/2026/04/bitwarden-cli-compromised-in-ongoing.html); [SecurityWeek](https://www.securityweek.com/bitwarden-npm-package-hit-in-supply-chain-attack/); [Unit 42](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/) |
| 2026-04-29 | SAP / `@cap-js/*` (Mini Shai-Hulud) | npm | ~572K weekly downloads combined | `mbt@1.2.48`, `@cap-js/db-service@2.10.1`, `@cap-js/postgres@2.2.2`, `@cap-js/sqlite@2.2.2` | Worm pattern; harvests AWS/GCP/Azure/k8s/Vault/GitHub/npm credentials | [The Hacker News](https://thehackernews.com/2026/04/sap-npm-packages-compromised-by-mini.html); [The Register](https://www.theregister.com/2026/04/30/supply_chain_attacks_sap_npm_packages/) |
| 2026-04-30 | Intercom and lightning | npm | 4 versions | `intercom-client@7.0.4`, `intercom-client@7.0.5`, `lightning@2.6.2`, `lightning@2.6.3` | Same payload as SAP wave | (linked from SAP postmortem) |
| 2026-04-30 | PyTorch Lightning (Mini Shai-Hulud) | PyPI | 2 versions, quarantined ~42 minutes after publish | `pytorch-lightning@2.6.2`, `pytorch-lightning@2.6.3` (clean: `2.6.1`) | Stolen PyPI credentials; obfuscated payload in a hidden `_runtime` directory executes on import; plants persistence hooks targeting Claude Code and VS Code (among the first malware to target AI coding agents) | [GHSA-w37p-236h-pfx3](https://github.com/Lightning-AI/pytorch-lightning/security/advisories/GHSA-w37p-236h-pfx3); CVE-2026-44484; [Semgrep](https://semgrep.dev/blog/2026/malicious-dependency-in-pytorch-lightning-used-for-ai-training/); [Socket](https://socket.dev/blog/lightning-pypi-package-compromised) |
| 2026-05-11 | TanStack (Mini Shai-Hulud) | npm | 84 versions across 42 packages, 19:20-19:26 UTC, ~6 minute window | 42 `@tanstack/*` packages; e.g. `@tanstack/react-router@1.169.5`-`1.169.8` (patched at `1.169.9`); full list in GHSA | `pull_request_target` “Pwn Request”, GitHub Actions cache poisoning, and OIDC token theft from runner memory (`/proc/<pid>/mem`); TeamPCP | [GHSA-g7cv-rxg3-hmpx](https://github.com/advisories/GHSA-g7cv-rxg3-hmpx); CVE-2026-45321 (CVSS 9.6); [TanStack postmortem](https://tanstack.com/blog/npm-supply-chain-compromise-postmortem); [StepSecurity](https://www.stepsecurity.io/blog/mini-shai-hulud-is-back-a-self-spreading-supply-chain-attack-hits-the-npm-ecosystem); [Socket](https://socket.dev/blog/tanstack-npm-packages-compromised-mini-shai-hulud-supply-chain-attack); [Aikido](https://www.aikido.dev/blog/mini-shai-hulud-is-back-tanstack-compromised) |
| 2026-05-11 | TanStack worm cross-ecosystem | PyPI | 2 packages | `mistralai@2.4.6`, `guardrails-ai@0.10.1` | Stolen CI/CD tokens from the npm wave propagated to PyPI | [GHSA-wx9m-wx4f-4cmg](https://github.com/advisories/GHSA-wx9m-wx4f-4cmg) (`mistralai`); [GHSA-xmpw-2vmm-p4p6](https://github.com/advisories/GHSA-xmpw-2vmm-p4p6) / CVE-2026-45758 (`guardrails-ai`); same npm sources as the row above |
| 2026-05-14 | node-ipc credential stealer | npm | 3 versions, ~10M weekly downloads, all published within ~1 minute | `node-ipc@9.1.6`, `node-ipc@9.2.3`, `node-ipc@12.0.1` | Expired-domain re-registration (`atlantis-software.net`, expired 2025-01-10, re-registered 2026-05-07) to take over the dormant `atiertant` maintainer account; ~80 KB payload appended to `node-ipc.cjs` fires at `require()` (no install script); 90+ credential categories exfiltrated via DNS TXT queries to `sh.azurestaticprovider.net` | [Socket](https://socket.dev/blog/node-ipc-package-compromised); [Snyk](https://snyk.io/blog/malicious-node-ipc-versions-published-npm/); [Datadog](https://securitylabs.datadoghq.com/articles/node-ipc-npm-malware-analysis/); [BleepingComputer](https://www.bleepingcomputer.com/news/security/popular-node-ipc-npm-package-compromised-to-steal-credentials/) |
| 2026-05-18..21 | Megalodon / `@tiledesk/tiledesk-server` | npm | Mass GitHub repo poisoning (~5,561 repos, ~5,718 commits in a 6-hour window); at least 1 npm package | `@tiledesk/tiledesk-server@2.18.6`, `2.18.7`, `2.18.9`, `2.18.10`, `2.18.11`, `2.18.12` (clean: `2.18.5`) | Automated mass injection of malicious GitHub Actions workflows (base64 bash) across thousands of repos using forged author identities; the legitimate maintainer published the npm package from the poisoned source unknowingly; secret exfil to `216.126.225.129:8443` | [GHSA-5vfv-hpg7-77hj](https://github.com/advisories/GHSA-5vfv-hpg7-77hj); [SafeDep](https://safedep.io/megalodon-mass-github-repo-backdooring-ci-workflows/); [StepSecurity](https://www.stepsecurity.io/blog/megalodon-mass-github-actions-secret-exfiltration-across-5-500-public-repositories); [The Hacker News](https://thehackernews.com/2026/05/megalodon-github-attack-targets-5561.html) |
| 2026-05-19 | @antv ecosystem (Mini Shai-Hulud) | npm | 639 malicious versions across 323 packages; 640 packages removed; 61,274 npm tokens invalidated; ~22-minute publish burst | `@antv/g@6.4.1`, `@antv/g@6.5.1`, `echarts-for-react@3.1.7`, `size-sensor@1.0.4` (full list via GitHub Advisory DB search `type:malware` for the `atool`-maintained scope) | Compromised `atool` maintainer account; **first known forged Sigstore / SLSA provenance** (worm calls Fulcio and Rekor at runtime so packages show a valid “verified” badge); `preinstall` worm that scrapes runner-process memory for secrets; C2 `t.m-kosche[.]com:443` | [Microsoft](https://www.microsoft.com/en-us/security/blog/2026/05/20/mini-shai-hulud-compromised-antv-npm-packages-enable-ci-cd-credential-theft/); [GHSA-6fr3-r6r6-h4h9](https://github.com/advisories/GHSA-6fr3-r6r6-h4h9); [Socket](https://socket.dev/blog/antv-packages-compromised); [Snyk](https://snyk.io/blog/mini-shai-hulud-antv-npm-supply-chain-attack/) |
| 2026-05-19 | Microsoft `durabletask` (TeamPCP Wave 4) | PyPI | 3 versions, ~417K monthly downloads, 35-minute publish window | `durabletask@1.4.1`, `durabletask@1.4.2`, `durabletask@1.4.3` (clean: `1.4.0`) | PyPI token stolen in an earlier GitHub breach; modified builds uploaded via twine with no matching tags/commits/CI runs; in-source dropper fetches `rope.pyz` second-stage credential stealer and worm (propagates via AWS SSM and `kubectl exec`) | [Wiz](https://www.wiz.io/blog/durabletask-teampcp-supply-chain-attack); [Snyk](https://snyk.io/blog/durabletask-pypi-supply-chain-attack/); [Endor Labs](https://www.endorlabs.com/learn/trojanized-microsoft-sdk-durabletask-1-4-1-through-1-4-3-deliver-credential-stealing-malware); [SafeDep](https://safedep.io/malicious-durabletask-pypi-supply-chain-attack/) |
| 2026-05-19 (reported; weaponized 2023-08-19) | `shopsprint/decimal` typosquat | Go modules | 1 module; ~33-month dwell time; repo removed but module still served by `proxy.golang.org` | `github.com/shopsprint/decimal@v1.3.3` | Single-letter typosquat of `github.com/shopspring/decimal`; malicious `init()` opens a DNS-TXT C2 channel to a dynamic-DNS subdomain and passes responses to `os/exec`; persists via Go module proxy caching (same persistence class as the BoltDB row) | [Socket](https://socket.dev/blog/popular-go-decimal-library-typosquat-dns-backdoor); [GBHackers](https://gbhackers.com/single-letter-go-module-typosquat/); [CyberSecurityNews](https://cybersecuritynews.com/hackers-use-single-letter-go-module-typosquat/) |
| 2026-05-19..24 | TrapDoor | npm | 21 packages, 335 versions | `crypto-credential-scanner`, `wallet-backup-verifier`, `defi-threat-scanner`, `eth-wallet-sentinel`, `llm-context-compressor`, `prompt-engineering-toolkit`, `model-switch-router` (full list in refs) | Impersonated crypto/DeFi and AI developer utilities; `postinstall` runs `trap-core.js`; **plants `.cursorrules` and `CLAUDE.md` carrying instructions hidden in zero-width Unicode (U+200B/200C/200D/FEFF) that tell the coding agent to run a “security scan” which exfiltrates local secrets**; seeded by documentation PRs to LangChain, LlamaIndex, MetaGPT, browser-use, OpenHands | [The Hacker News](https://thehackernews.com/2026/05/trapdoor-supply-chain-attack-spreads.html); [Phoenix Security](https://phoenix.security/trapdoor-supply-chain-ai-poisoning-npm-pypi-crates/) |
| 2026-05-19..24 | TrapDoor cross-ecosystem | PyPI | 7 packages, 10 versions | `cryptowallet-safety`, `defi-risk-scanner`, `eth-security-auditor`, `solidity-build-guard`, `env-loader-cli`, `git-config-sync`, `data-pipeline-check` | Import-time execution (no install script): fetches a remote JS payload from `ddjidd564.github.io` and runs it via `node -e` | [The Hacker News](https://thehackernews.com/2026/05/trapdoor-supply-chain-attack-spreads.html); [Phoenix Security](https://phoenix.security/trapdoor-supply-chain-ai-poisoning-npm-pypi-crates/) |
| 2026-05-19..24 | TrapDoor cross-ecosystem | crates.io | 6 crates, 6 versions | `sui-move-build-helper`, `sui-framework-helpers`, `sui-sdk-build-utils`, `move-analyzer-build`, `move-compiler-tools`, `move-project-builder` | `build.rs` fires during `cargo build` before any library code runs; locates Sui/Aptos wallet keystores, XOR-encrypts with key `cargo-build-helper-2026`, exfiltrates to GitHub Gists | [The Hacker News](https://thehackernews.com/2026/05/trapdoor-supply-chain-attack-spreads.html); [Phoenix Security](https://phoenix.security/trapdoor-supply-chain-ai-poisoning-npm-pypi-crates/) |
| 2026-06-01 | Miasma (Shai-Hulud variant) | npm | 32 releases across the `@redhat-cloud-services` scope; ~80-117K weekly downloads in scope | `@redhat-cloud-services/frontend-components@7.7.2`, `@7.7.3`, `@7.7.5`, `@redhat-cloud-services/rbac-client@9.0.3`, `@9.0.4`, `@9.0.6`, `@redhat-cloud-services/insights-client@4.0.4`, `@4.0.5`, `@4.0.7` (29 further packages in refs) | ~4.2 MB obfuscated `preinstall` payload (`eval()` and ROT decoding); sweeps GitHub tokens, SSH keys, GCP/Azure identities and CI/CD secrets; republishes via stolen GitHub OIDC tokens **with valid SLSA provenance attestations** | [Wiz](https://www.wiz.io/blog/miasma-supply-chain-attack-targeting-redhat-npm-packages); [Orca](https://orca.security/resources/blog/red-hat-npm-supply-chain-attack/); [Harness](https://www.harness.io/blog/shai-hulud-miasma-inside-the-compromise-of-red-hats-packages) |
| 2026-06-03 | IronWorm | npm | 36-43 packages from the compromised `asteroiddao` account | `weavedb-sdk`, `weavedb-lite`, `weavedb-sdk-base`, `arnext`, `roidjs`, `zkjson`, `wao`, `cwao-tools`, `fpjson-lang` (full list in refs) | ~976 KB Rust ELF dropped by a `preinstall` hook; custom-modified UPX stub; **embedded eBPF kernel rootkit** hides processes and sockets; Tor hidden-service C2; sweeps 86 env vars and 20+ credential paths including **AI provider keys (Anthropic, OpenAI, Gemini, Cohere, Mistral, Groq, xAI)**; republishes via npm Trusted Publishing (OIDC) | [JFrog](https://research.jfrog.com/post/iron-worm-shai-hulud-rustier-cousin/); [SafeDep](https://safedep.io/ti/campaigns/ironworm/); [Dark Reading](https://www.darkreading.com/cyberattacks-data-breaches/rust-written-ironworm-npm-supply-chain) |
| 2026-06-04 | Miasma wave 2 (`binding.gyp`) | npm | Second wave of the row above | (same campaign; see refs for the wave-2 version list) | Dropped `postinstall` in favour of **`binding.gyp` executed by an implicit `node-gyp` build**, specifically to evade tooling that only monitors lifecycle-script fields | [Phoenix Security](https://phoenix.security/miasma-wave2-npm-supply-chain-bindingyp-zero-cve-2026/); [Unit 42](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/) |
| 2026-06-05 | Miasma / Azure repo poisoning | GitHub repos (cross-ecosystem) | 73 Microsoft repositories across 4 orgs disabled by GitHub in a 105-second automated sweep; `Azure/functions-action` outage broke CI/CD globally | Malicious commit to `Azure/durabletask` via a previously compromised contributor account; no `pkg@version` IOC (repo-level, not registry-level) | **Execution moved from install-time to open-time:** committed `.claude/settings.json` (Claude Code `SessionStart` hook) plus editor autostart config, firing a credential harvester when a developer or agent merely *opens the repo* in Claude Code, Gemini CLI, Cursor, or VS Code | [StepSecurity](https://www.stepsecurity.io/blog/miasma-worm-hits-microsoft-again-azure-functions-action-and-72-other-repositories-disabled-after-supply-chain-attack-targeting-ai-coding-agents); [Phoenix Security](https://phoenix.security/miasma-azure-hades-pypi-supply-chain-worm-2026/); [Rescana](https://www.rescana.com/post/miasma-worm-supply-chain-attack-73-microsoft-github-repositories-compromised-via-ai-coding-tools) |
| 2026-06-08 | Hades (Shai-Hulud lineage) | PyPI | 37 malicious wheels across 19-26 packages (counts differ by vendor); part of a 471-artifact npm+PyPI campaign | `embiggen@0.11.97`, `ensmallen@0.8.101`, `gpsea@0.9.14`, `pyphetools@0.9.120`, `phenopacket-store-toolkit@0.1.7`, `ppkt2synergy@0.1.1`, `langchain-core-mcp@1.4.2`, `@1.4.3`, `openai-mcp@2.41.1`, `@2.41.2`, `instructor-mcp@1.15.2`, `@1.15.3`, `tiktoken-mcp@0.13.1`, `@0.13.2`, `ray-mcp-server@0.2.1` | **`.pth` interpreter-startup hook, shipped inside wheels.** A `*-setup.pth` file (e.g. `langchain_core-setup.pth`) runs on *every* Python startup—no import of the package required and no sdist build involved, so `--only-binary` / `--no-build` do not help. Downloads Bun 1.3.13/1.3.14 and runs `_index.js`, which reads process memory directly (`/proc/<pid>/mem`, Mach APIs, `ReadProcessMemory`). Targets bioinformatics and MCP/AI tooling | [Socket](https://socket.dev/blog/mini-shai-hulud-miasma-and-hades-worms-target-bioinformatics-and-mcp-developers-via-malicious); [The Hacker News](https://thehackernews.com/2026/06/hades-pypi-attack-19-packages-poisoned.html); [Orca](https://orca.security/resources/blog/hades-pypi-supply-chain-attack/); [Dark Reading](https://www.darkreading.com/application-security/hades-campaign-pypi-shai-hulud) |
| 2026-08-04 | keyv / cacheable worm | npm | Counts differ because the registry changed during the campaign: SafeDep 2,234 versions / 444 packages; Aikido 1,381 versions / 868 packages; Socket 442 versions / 353 names. Reached 9 unrelated orgs (`@ornikar`, `@deliveroo`, `@servicetitan`, `@qlik`, `@onereach`, `@or-sdk`, `@arv-bedrock`, `@adminide-stack`) in ~30 min. `keyv` alone is ~127M weekly downloads | `keyv@6.0.0`, `cacheable@2.5.1`, `cacheable-request@13.0.20`, `flat-cache@6.1.24`, `file-entry-cache@11.1.7`, `cache-manager@7.2.10`, `@cacheable/net@2.1.1`, `@cacheable/node-cache@3.1.2`, `@cacheable/memory@2.2.1`, `@cacheable/utils@2.5.1`, `@thiennq/docs-viewer@1.6.2` (the `@keyv/*` adapters and the Keyv 5.x line were clean) | `preinstall` runs `setup.mjs`, which **downloads a standalone Bun 1.3.13 runtime unverified** and executes `Math_Symbol.js` (~728 KB, basE91-encoded). Harvests AWS/GCP/Azure metadata, Vault and Kubernetes tokens, npm and GitHub Actions OIDC secrets. Republishes via npm OIDC exchange and **generates DSSE attestations with Fulcio certs and Rekor entries**. Plants `.claude/settings.json` `SessionStart` and `.vscode/tasks.json` `folderOpen` autostart hooks. Installs a **revocation dead-man’s switch** (`~/.config/gh-token-monitor/`, LaunchAgent/systemd user unit) that polls GitHub every 60 s and `eval`s a remote handler when the token stops working | [Socket](https://socket.dev/blog/popular-npm-packages-in-the-keyv-and-cacheable-namespaces-compromised-in-active-supply-chain); [SafeDep](https://safedep.io/keyv-npm-supply-chain-compromise/); [Aikido](https://www.aikido.dev/blog/keyv-and-friends-compromised-in-npm-supply-chain-attack); [Wiz](https://www.wiz.io/blog/keyv-and-cacheable-npm-supply-chain-attack); [The Hacker News](https://thehackernews.com/2026/08/keyv-linked-npm-worm-poisons-hundreds.html) |

## Historical Incidents (Recognition Only)

Aged out of the Active Watch List: the mechanism is still worth recognising on sight,
but the malicious versions are long yanked and no longer turn up in a fresh resolve.
Per-version IOCs are deliberately not duplicated here.
`osv-scanner` and the [systems of record](README.md#authoritative-sources) cover these
incidents completely, so a scan of an old lockfile should use those, not this file.

| Date | Name | Ecosystem | Pattern worth recognising | References |
| --- | --- | --- | --- | --- |
| 2021-11..2025-02 | BoltDB typosquat | Go modules | Module-proxy caching served a removed typosquat for ~3 years; deleting the source repository does not purge `proxy.golang.org` | [Socket](https://socket.dev/blog/malicious-package-exploits-go-module-proxy-caching-for-persistence); [Snyk](https://snyk.io/blog/go-malicious-package-alert/) |
| 2022-05 | rustdecimal typosquat | crates.io | Typosquat with a runtime payload in an innocuous-looking API call, targeting GitLab CI | [Rust Blog](https://blog.rust-lang.org/2022/05/10/malicious-crate-rustdecimal/); [RUSTSEC-2022-0042](https://rustsec.org/advisories/RUSTSEC-2022-0042.html) |
| 2022-05-14 | ctx account takeover | PyPI | Expired-domain re-registration to take over a dormant maintainer account; malicious for ~10 days—the slow-detection tail the 14-day cool-off is sized against | [The Hacker News](https://thehackernews.com/2022/05/pypi-package-ctx-and-php-library-phpass.html); [Sonatype](https://www.sonatype.com/blog/pypi-package-ctx-compromised-are-you-at-risk) |
| 2022-12-25 | PyTorch torchtriton | PyPI | Dependency confusion: public package outversioned a private-index name; DNS-tunnel exfiltration | [PyTorch blog](https://pytorch.org/blog/compromised-nightly-dependency/); [SentinelOne](https://www.sentinelone.com/blog/pytorch-dependency-torchtriton-supply-chain-attack/) |
| 2024-12-04 | Ultralytics YOLO cryptominer | PyPI | GitHub Actions `pull_request_target` script injection stole a PyPI token; cryptominer shipped in the wheel | [PyPI blog](https://blog.pypi.org/posts/2024-12-11-ultralytics-attack-analysis/); [Wiz](https://www.wiz.io/blog/ultralytics-ai-library-hacked-via-github-for-cryptomining) |
| 2025-01..02 | hypert / layout typosquats | Go modules | Batch typosquats of niche libraries carrying an obfuscated RCE loader | [Socket](https://socket.dev/blog/typosquatted-go-packages-deliver-malware-loader); [The Hacker News](https://thehackernews.com/2025/03/seven-malicious-go-packages-found.html) |
| 2025-02 | Fake `x/crypto` (Rekoobe) | Go modules | Impersonated `golang.org/x/crypto`; hooked `ReadPassword()` and deployed an APT backdoor | [Socket](https://socket.dev/blog/malicious-go-crypto-module-steals-passwords-and-deploys-rekoobe-backdoor); [The Hacker News](https://thehackernews.com/2026/02/malicious-go-crypto-module-steals.html) |
| 2025-05 | Disk-wiper modules | Go modules | Typosquats carrying a destructive disk-wiper rather than an infostealer | [Socket](https://socket.dev/blog/wget-to-wipeout-malicious-go-modules-fetch-destructive-payload); [BleepingComputer](https://www.bleepingcomputer.com/news/security/linux-wiper-malware-hidden-in-malicious-go-modules-on-github/) |
| 2025-06 | MongoDB qmgo typosquat | Go modules | Single-letter username typosquat; malicious behaviour hidden in the client constructor | [GitLab](https://about.gitlab.com/blog/gitlab-catches-mongodb-go-module-supply-chain-attack/) |

## Contextual Incidents (Unverified / Pending Verification)

The campaigns below have been mentioned in trusted feeds but lack the per-version,
multi-source citations required for the actionable-IOC table.
Treat them as situational awareness, **not** as actionable IOCs—there is no grep-able
string here, and the hardening cool-off does not specifically target them.
If you have verified package@version, dates, and at least two independent references,
promote the row into the Active Watch List and remove it here.

| Date (approx.) | Name | Ecosystem | What is known | What is missing |
| --- | --- | --- | --- | --- |
| 2026-05 (reported) | BufferZoneCorp sleeper modules | Go modules and RubyGems | 9 Go modules and 7 Ruby gems under `github.com/BufferZoneCorp/*`, impersonating popular libraries (`go-retryablehttp`, `go-envconfig`); two-phase “sleeper” published clean then weaponized to tamper with `GOPROXY` / `go.sum` and plant SSH keys; reported by Socket. All blocked. | Exact `module@version` strings (not publicly published); independent technical analysis beyond the single primary source. |

## How To Use This Table

- **Spot-check installed packages.** Grep lockfiles and installed trees for any
  `pkg@version` in the Active Watch List.
  The npm hardening guide includes a ready-made grep template in `hardening-npm.md` →
  “Compromise Assessment”.
  The PyPI hardening guide includes an equivalent in `hardening-pypi.md` → “Compromise
  Assessment”. For lockfiles older than the active window, run `osv-scanner` against the
  systems of record instead of grepping this file; Historical rows deliberately carry no
  IOCs.
- **Reference, do not duplicate.** Per-ecosystem hardening and research docs link to
  this table rather than reproducing it.
  New rows enter the Active Watch List first.
- **Open an audit-log entry** if any installed package matches; see
  `supply-chain-audit-log-template.md`.

## Reading Notes

- “Live X hours” is the time between malicious publish and yank/deprecation.
  After that window the affected `package@version` is no longer the registry’s latest
  but remains in any lockfile that captured it.
- Versions outside the listed ranges are presumed safe unless a follow-up advisory says
  otherwise.
- Some rows reference an OSV `MAL-*` ID even when the canonical advisory is filed under
  a GHSA, both IDs are valid lookups in the OSV API.
- A “verified” provenance badge is no longer proof of safety.
  The 2026-05-19 @antv worm forged valid Sigstore / SLSA attestations at runtime, and by
  June-August 2026 this was routine: Miasma, IronWorm, and the keyv worm all republished
  through stolen OIDC credentials with attestations that verify.
  A valid attestation confirms *which pipeline* produced a package, not that the
  pipeline was uncompromised.
  Treat provenance as one signal, not a guarantee; see
  [`guidelines/hardening-ci-cd.md`](guidelines/hardening-ci-cd.md).

### The Three Trigger Classes

Rows in this table no longer share a single execution moment.
Grouping them by *when the payload runs* is what determines which control stops them, so
read the Vector column for the trigger before assuming a control applies.

| Trigger | Runs when | Example rows | What stops it |
| --- | --- | --- | --- |
| **Install-time** | `npm install`, `pip install`, `cargo build` | qix, Shai-Hulud, Miasma, keyv, TrapDoor (npm/crates) | Cool-off window; `ignore-scripts` / npm 12 `allowScripts`; `--only-binary`; lockfile discipline |
| **Load-time** | `require()`, `import`, or *any* interpreter start | node-ipc, LiteLLM, TrapDoor (PyPI), **Hades (`.pth`)** | Cool-off only. Script-disabling and wheel-only policies do **not** help; needs `.pth` auditing and sandboxed first runs |
| **Open-time** | A developer or AI agent opens the repo or folder | **Miasma / Azure repos**, **keyv**, **TrapDoor (`CLAUDE.md`)** | No package-manager control applies at all. Needs workspace-trust settings and an agent-config review before opening; see [`guidelines/hardening-agent-workspaces.md`](guidelines/hardening-agent-workspaces.md) |

Open-time is the 2026-Q2 innovation and the most important one for agent operators: the
malicious code is committed to a **git repository**, not published to a registry, so the
cool-off window, the lockfile, and every install-side flag in this repo are irrelevant
to it.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
