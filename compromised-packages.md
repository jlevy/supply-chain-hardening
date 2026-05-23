# Compromised Packages

**Last updated:** 2026-05-23

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

## Table (Actionable IOCs)

Every row below has either an exact `pkg@version` IOC, a complete affected-package list
at the linked URL, or a canonical GHSA / RUSTSEC ID that resolves to one.
Defenders running a scan can use this table directly without follow-up research.

| Date | Name | Ecosystem | Scale | Affected `pkg@version` (representative; full list at the linked source) | Vector | References |
| --- | --- | --- | --- | --- | --- | --- |
| 2021-11..2025-02 | BoltDB typosquat | Go modules | 1 module, cached in module proxy ~3 years | `github.com/boltdb-go/bolt@v1.3.1` | Typosquat of `boltdb/bolt`; module proxy caching hid removal | [Socket](https://socket.dev/blog/malicious-package-exploits-go-module-proxy-caching-for-persistence); [Snyk](https://snyk.io/blog/go-malicious-package-alert/); [The Register](https://www.theregister.com/2025/02/04/golang_supply_chain_attack/) |
| 2022-05 | rustdecimal typosquat | crates.io | 1 crate, <500 downloads | `rustdecimal@1.23.1` | Typosquat of `rust_decimal`; runtime payload in `Decimal::new` targeting GitLab CI | [Rust Blog](https://blog.rust-lang.org/2022/05/10/malicious-crate-rustdecimal/); [RUSTSEC-2022-0042](https://rustsec.org/advisories/RUSTSEC-2022-0042.html); [GHSA-7pwq-f4pq-78gm](https://github.com/advisories/GHSA-7pwq-f4pq-78gm); [Sonatype](https://www.sonatype.com/blog/this-week-in-malware-may-13th-edition) |
| 2022-05-14 | ctx account takeover | PyPI | 1 package, ~27K downloads in 10-day window | `ctx` (all versions published 2022-05-14 through 2022-05-24) | Expired-domain re-registration; password reset; env-var exfil to Heroku endpoint | [The Hacker News](https://thehackernews.com/2022/05/pypi-package-ctx-and-php-library-phpass.html); [Sonatype](https://www.sonatype.com/blog/pypi-package-ctx-compromised-are-you-at-risk); [BleepingComputer](https://www.bleepingcomputer.com/news/security/popular-python-and-php-libraries-hijacked-to-steal-aws-keys/) |
| 2022-12-25 | PyTorch torchtriton | PyPI | 1 package, ~2,700 downloads in 5-day window; nightly builds only | `torchtriton@2.0.0` | Dependency confusion; public PyPI package with higher version than private index; exfil via DNS tunneling to `*.h4ck.cfd` | [PyTorch blog](https://pytorch.org/blog/compromised-nightly-dependency/); [SentinelOne](https://www.sentinelone.com/blog/pytorch-dependency-torchtriton-supply-chain-attack/); [ReversingLabs](https://www.reversinglabs.com/blog/pytorch-supply-chain-attack-dependency-confusion-burns-devops) |
| 2024-12-04 | Ultralytics YOLO cryptominer | PyPI | 4 versions, ~60M monthly downloads | `ultralytics@8.3.41`, `ultralytics@8.3.42`, `ultralytics@8.3.45`, `ultralytics@8.3.46` | GitHub Actions `pull_request_target` script injection; stolen PyPI token; XMRig cryptominer in wheel | [PyPI blog](https://blog.pypi.org/posts/2024-12-11-ultralytics-attack-analysis/); [ReversingLabs](https://www.reversinglabs.com/blog/compromised-ultralytics-pypi-package-delivers-crypto-coinminer); [Snyk](https://snyk.io/blog/ultralytics-ai-pwn-request-supply-chain-attack/); [Wiz](https://www.wiz.io/blog/ultralytics-ai-library-hacked-via-github-for-cryptomining) |
| 2025-01..02 | hypert / layout typosquats | Go modules | 7 modules | `github.com/shallowmulti/hypert`, `github.com/shadowybulk/hypert`, `github.com/belatedplanet/hypert`, `github.com/thankfulmai/hypert`, `github.com/vainreboot/layout`, `github.com/ornatedoctrin/layout`, `github.com/utilizedsun/layout` | Typosquats of `areknoster/hypert` and `loov/layout`; obfuscated RCE loader | [Socket](https://socket.dev/blog/typosquatted-go-packages-deliver-malware-loader); [The Hacker News](https://thehackernews.com/2025/03/seven-malicious-go-packages-found.html) |
| 2025-02 | Fake `x/crypto` (Rekoobe) | Go modules | 1 module | `github.com/xinfeisoft/crypto@v0.15.0` | Impersonates `golang.org/x/crypto`; hooks `ReadPassword()` to exfil creds; deploys Rekoobe backdoor (APT31) | [Socket](https://socket.dev/blog/malicious-go-crypto-module-steals-passwords-and-deploys-rekoobe-backdoor); [The Hacker News](https://thehackernews.com/2026/02/malicious-go-crypto-module-steals.html) |
| 2025-05 | Disk-wiper modules | Go modules | 3 modules | `github.com/truthfulpharm/prototransform`, `github.com/blankloggia/go-mcp`, `github.com/steelpoor/tlsproxy` | Typosquats; `dd if=/dev/zero of=/dev/sda` wiper on Linux | [Socket](https://socket.dev/blog/wget-to-wipeout-malicious-go-modules-fetch-destructive-payload); [BleepingComputer](https://www.bleepingcomputer.com/news/security/linux-wiper-malware-hidden-in-malicious-go-modules-on-github/) |
| 2025-06 | MongoDB qmgo typosquat | Go modules | 2 variants | `github.com/qiniiu/qmgo`, `github.com/qiiniu/qmgo` | Typosquat of `qiniu/qmgo` (extra `i` in username); malicious `NewClient` | [GitLab](https://about.gitlab.com/blog/gitlab-catches-mongodb-go-module-supply-chain-attack/) |
| 2025-08 | Nx packages | npm | ~10 packages | `nx@21.5.0`-`21.5.3`, `@nx/devkit@21.5.0`-`21.5.3`, `@nx/enterprise-cloud@3.2.0`, `@nx/eslint@21.5.0`, `@nx/js@21.5.0`/`21.5.1`, `@nx/key@3.2.0`, `@nx/node@21.5.0`, `@nx/workspace@21.5.0` | Maintainer-account compromise; stole npm + GitHub tokens | OSV; Snyk |
| 2025-09-08 | “qix” maintainer phish | npm | 18+ packages, ~billions of weekly downloads combined, malicious versions live ~2 hours | `ansi-styles@6.2.2`, `debug@4.4.2`, `chalk@5.6.1`, `supports-color@10.2.1`, `strip-ansi@7.1.1`, `ansi-regex@6.2.1`, `wrap-ansi@9.0.1`, `color-convert@3.1.1`, `color-name@2.0.1`, `is-arrayish@0.3.3`, `slice-ansi@7.1.1`, `error-ex@1.3.3`, `simple-swizzle@0.2.3`, `supports-hyperlinks@4.1.1`, `chalk-template@1.1.1`, `backslash@0.2.1`, `color-string@2.1.1`, `has-ansi@6.0.1`, `proto-tinker-wc@0.1.87` | Phishing via fake `npmjs.help` 2FA-reset email; collected user/pass/TOTP | OSV (`MAL-2025-46969`, `MAL-2025-46974`); [Socket](https://socket.dev/blog/npm-author-qix-compromised-in-major-supply-chain-attack); [StepSecurity](https://www.stepsecurity.io/blog/20-popular-npm-packages-compromised-chalk-debug-strip-ansi-color-convert-wrap-ansi) |
| 2025-09 | faster_log / async_println crypto-key theft | crates.io | 2 crates, ~8,424 combined downloads | `faster_log` (all versions by `rustguruman`), `async_println` (all versions by `dumbnbased`) | Typosquat of `fast_log`; runtime exfil of Solana/Ethereum private keys via Cloudflare Workers | [Rust Blog](https://blog.rust-lang.org/2025/09/24/crates.io-malicious-crates-fasterlog-and-asyncprintln/); [Socket](https://socket.dev/blog/two-malicious-rust-crates-impersonate-popular-logger-to-steal-wallet-keys); [The Hacker News](https://thehackernews.com/2025/09/malicious-rust-crates-steal-solana-and.html) |
| 2025-09-15 | Shai-Hulud 1.0 worm | npm | 500+ packages, ~180 confirmed | `@ctrl/tinycolor@4.1.1`, `@ctrl/tinycolor@4.1.2` (initial vector), `ngx-bootstrap`, `ng2-file-upload`, `angulartics2`, many `@ctrl/*` | Self-replicating worm; stolen tokens auto-republished to other packages owned by victim | [Sysdig](https://www.sysdig.com/blog/shai-hulud-the-novel-self-replicating-worm-infecting-hundreds-of-npm-packages); [CISA](https://www.cisa.gov/news-events/cybersecurity-advisories/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem); [Unit 42](https://unit42.paloaltonetworks.com/npm-supply-chain-attack/) |
| 2025-11-24 | Shai-Hulud 2.0 | npm | 796 packages, ~25K repos, ~350 maintainers | Full IOC list: `https://blog.ehsan.it/shai-hulud-v2-ioc.json` | Worm + `preinstall` script invoking `setup_bun.js` / `bun_environment.js`; registers self-hosted GitHub runner named `SHA1HULUD` for persistence | [Datadog Security Labs](https://securitylabs.datadoghq.com/articles/shai-hulud-2.0-npm-worm/); [Wiz](https://www.wiz.io/blog/shai-hulud-2-0-ongoing-supply-chain-attack); [Netskope](https://www.netskope.com/blog/shai-hulud-2-0-aggressive-automated-one-of-fastest-spreading-npm-supply-chain-attacks-ever-observed) |
| 2025-12 | evm-units / uniswap-utils Web3 targeting | crates.io | 2 crates, ~14,400 combined downloads | `evm-units` (all versions by `ablerust`), `uniswap-utils` (14 versions) | Transitive-dep facade; OS-specific binary download and execution via `#[ctor::ctor]` | [Rust Blog](https://blog.rust-lang.org/2025/12/03/crates.io-malicious-crates-evm-units-and-uniswap-utils/); [Socket](https://socket.dev/blog/malicious-rust-crate-evm-units-serves-cross-platform-payloads); [The Hacker News](https://thehackernews.com/2025/12/malicious-rust-crate-delivers-os.html) |
| 2025-12 | finch-rst / sha-rst credential theft | crates.io | 3 crates, ~61 combined downloads | `finch-rst`, `sha-rst`, `finch_cli_rust` | Typosquat of `finch`/`finch_cli`; credential exfiltration payload in `sha-rst` | [RUSTSEC-2025-0150](https://rustsec.org/advisories/RUSTSEC-2025-0150.html); [RUSTSEC-2025-0151](https://rustsec.org/advisories/RUSTSEC-2025-0151.html); [RUSTSEC-2025-0152](https://rustsec.org/advisories/RUSTSEC-2025-0152.html) |
| 2026-02..03 | Time-utility .env exfiltration campaign | crates.io | 5 crates | `chrono_anchor`, `dnp3times`, `time_calibrator`, `time_calibrators`, `time-sync` | Impersonation of time utilities; `.env` exfiltration; `chrono_anchor` obfuscated | [Socket](https://socket.dev/blog/5-malicious-rust-crates-posed-as-time-utilities-to-exfiltrate-env-files); [The Hacker News](https://thehackernews.com/2026/03/five-malicious-rust-crates-and-ai-bot.html) |
| 2026-03-20..04-08 | CanisterWorm / CanisterSprawl (post-Trivy) | npm | 141 malicious versions across 66+ packages; CanisterSprawl wave ~8,424 weekly downloads combined | `@automagik/genie@4.260421.33`-`@automagik/genie@4.260421.39`, `pgserve@1.1.11`, `pgserve@1.1.12`, `pgserve@1.1.13` (CanisterSprawl); 47+ packages incl `@opengov/*` (initial CanisterWorm wave) | npm fallout of the Aqua Trivy GitHub Action compromise (same root cause as the LiteLLM row below); self-replicating worm whose `deploy.js` harvests npm tokens and republishes, using a decentralized (IPFS/ICP-canister) C2 for resilience; TeamPCP | [The Hacker News](https://thehackernews.com/2026/03/trivy-supply-chain-attack-triggers-self.html); [Aikido](https://www.aikido.dev/blog/teampcp-deploys-worm-npm-trivy-compromise); [Mend](https://www.mend.io/blog/canisterworm-the-self-spreading-npm-attack-that-uses-a-decentralized-server-to-stay-alive/); [Socket](https://socket.dev/blog/namastex-npm-packages-compromised-canisterworm) |
| 2026-03-24 | LiteLLM / TeamPCP | PyPI | 2 versions, ~119K downloads in ~40 minutes; ~95M monthly downloads | `litellm@1.82.7`, `litellm@1.82.8` | Stolen PyPI token via compromised Trivy GitHub Action in CI/CD; credential harvesting + systemd backdoor; TeamPCP | [PyPI incident report](https://blog.pypi.org/posts/2026-04-02-incident-report-litellm-telnyx-supply-chain-attack/); [Datadog Security Labs](https://securitylabs.datadoghq.com/articles/litellm-compromised-pypi-teampcp-supply-chain-campaign/); [Snyk](https://snyk.io/blog/poisoned-security-scanner-backdooring-litellm/); GHSA-5mg7-485q-xm76 |
| 2026-03-31 | Axios | npm | 2 versions, ~70M weekly downloads | `axios@1.14.1`, `axios@0.30.4` | Sapphire Sleet (DPRK); pulls 2nd-stage RAT | [CISA](https://www.cisa.gov/news-events/cybersecurity-advisories/2026/04/20/supply-chain-compromise-impacts-axios-node-package-manager); [Microsoft Security](https://www.microsoft.com/en-us/security/blog/2026/04/01/mitigating-the-axios-npm-supply-chain-compromise/); [Mandiant](https://cloud.google.com/blog/topics/threat-intelligence/north-korea-threat-actor-targets-axios-npm-package) |
| 2026-04 | mysten-metrics build.rs exfiltration | crates.io | 1 crate | `mysten-metrics@9.0.3` | Malicious `build.rs` runs `env`/`cat`/`ls -R` at compile time, exfils via HTTP POST | [GHSA-G38R-8GMR-GHRF](https://github.com/advisories/GHSA-G38R-8GMR-GHRF); RUSTSEC-2026-0107 |
| 2026-04-22 | `@bitwarden/cli` (TeamPCP / Checkmarx) | npm | 1 version, live ~17:57-19:30 ET (~93 min), ~334 downloads | `@bitwarden/cli@2026.4.0` (clean: `2026.4.1`; last clean before: `2026.3.0`) | Malicious build published through the npm delivery path during the Checkmarx supply-chain incident; `bw1.js` harvests GitHub/npm tokens, `.ssh`, `.env`, shell history, and cloud secrets, exfiltrates to private domains and GitHub commits, and self-propagates by backdooring packages the victim can publish | [Bitwarden statement](https://community.bitwarden.com/t/bitwarden-statement-on-checkmarx-supply-chain-incident/96127); [The Hacker News](https://thehackernews.com/2026/04/bitwarden-cli-compromised-in-ongoing.html); [SecurityWeek](https://www.securityweek.com/bitwarden-npm-package-hit-in-supply-chain-attack/); [Unit 42](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/) |
| 2026-04-29 | SAP / `@cap-js/*` (Mini Shai-Hulud) | npm | ~572K weekly downloads combined | `mbt@1.2.48`, `@cap-js/db-service@2.10.1`, `@cap-js/postgres@2.2.2`, `@cap-js/sqlite@2.2.2` | Worm pattern; harvests AWS/GCP/Azure/k8s/Vault/GitHub/npm credentials | [The Hacker News](https://thehackernews.com/2026/04/sap-npm-packages-compromised-by-mini.html); [The Register](https://www.theregister.com/2026/04/30/supply_chain_attacks_sap_npm_packages/) |
| 2026-04-30 | Intercom + lightning | npm | 4 versions | `intercom-client@7.0.4`, `intercom-client@7.0.5`, `lightning@2.6.2`, `lightning@2.6.3` | Same payload as SAP wave | (linked from SAP postmortem) |
| 2026-04-30 | PyTorch Lightning (Mini Shai-Hulud) | PyPI | 2 versions, quarantined ~42 minutes after publish | `pytorch-lightning@2.6.2`, `pytorch-lightning@2.6.3` (clean: `2.6.1`) | Stolen PyPI credentials; obfuscated payload in a hidden `_runtime` directory executes on import; plants persistence hooks targeting Claude Code and VS Code (among the first malware to target AI coding agents) | [GHSA-w37p-236h-pfx3](https://github.com/Lightning-AI/pytorch-lightning/security/advisories/GHSA-w37p-236h-pfx3); CVE-2026-44484; [Semgrep](https://semgrep.dev/blog/2026/malicious-dependency-in-pytorch-lightning-used-for-ai-training/); [Socket](https://socket.dev/blog/lightning-pypi-package-compromised) |
| 2026-05-11 | TanStack (Mini Shai-Hulud) | npm | 84 versions across 42 packages, 19:20-19:26 UTC, ~6 minute window | 42 `@tanstack/*` packages; e.g. `@tanstack/react-router@1.169.5`-`1.169.8` (patched at `1.169.9`); full list in GHSA | `pull_request_target` “Pwn Request” + GitHub Actions cache poisoning + OIDC token theft from runner memory (`/proc/<pid>/mem`); TeamPCP | [GHSA-g7cv-rxg3-hmpx](https://github.com/advisories/GHSA-g7cv-rxg3-hmpx); CVE-2026-45321 (CVSS 9.6); [TanStack postmortem](https://tanstack.com/blog/npm-supply-chain-compromise-postmortem); [StepSecurity](https://www.stepsecurity.io/blog/mini-shai-hulud-is-back-a-self-spreading-supply-chain-attack-hits-the-npm-ecosystem); [Socket](https://socket.dev/blog/tanstack-npm-packages-compromised-mini-shai-hulud-supply-chain-attack); [Aikido](https://www.aikido.dev/blog/mini-shai-hulud-is-back-tanstack-compromised) |
| 2026-05-11 | TanStack worm cross-ecosystem | PyPI | 2 packages | `mistralai@2.4.6`, `guardrails-ai@0.10.1` | Stolen CI/CD tokens from the npm wave propagated to PyPI | [GHSA-wx9m-wx4f-4cmg](https://github.com/advisories/GHSA-wx9m-wx4f-4cmg) (`mistralai`); [GHSA-xmpw-2vmm-p4p6](https://github.com/advisories/GHSA-xmpw-2vmm-p4p6) / CVE-2026-45758 (`guardrails-ai`); same npm sources as the row above |
| 2026-05-14 | node-ipc credential stealer | npm | 3 versions, ~10M weekly downloads, all published within ~1 minute | `node-ipc@9.1.6`, `node-ipc@9.2.3`, `node-ipc@12.0.1` | Expired-domain re-registration (`atlantis-software.net`, expired 2025-01-10, re-registered 2026-05-07) to take over the dormant `atiertant` maintainer account; ~80 KB payload appended to `node-ipc.cjs` fires at `require()` (no install script); 90+ credential categories exfiltrated via DNS TXT queries to `sh.azurestaticprovider.net` | [Socket](https://socket.dev/blog/node-ipc-package-compromised); [Snyk](https://snyk.io/blog/malicious-node-ipc-versions-published-npm/); [Datadog](https://securitylabs.datadoghq.com/articles/node-ipc-npm-malware-analysis/); [BleepingComputer](https://www.bleepingcomputer.com/news/security/popular-node-ipc-npm-package-compromised-to-steal-credentials/) |
| 2026-05-18..21 | Megalodon / `@tiledesk/tiledesk-server` | npm | Mass GitHub repo poisoning (~5,561 repos, ~5,718 commits in a 6-hour window); at least 1 npm package | `@tiledesk/tiledesk-server@2.18.6`, `2.18.7`, `2.18.9`, `2.18.10`, `2.18.11`, `2.18.12` (clean: `2.18.5`) | Automated mass injection of malicious GitHub Actions workflows (base64 bash) across thousands of repos using forged author identities; the legitimate maintainer published the npm package from the poisoned source unknowingly; secret exfil to `216.126.225.129:8443` | [GHSA-5vfv-hpg7-77hj](https://github.com/advisories/GHSA-5vfv-hpg7-77hj); [SafeDep](https://safedep.io/megalodon-mass-github-repo-backdooring-ci-workflows/); [StepSecurity](https://www.stepsecurity.io/blog/megalodon-mass-github-actions-secret-exfiltration-across-5-500-public-repositories); [The Hacker News](https://thehackernews.com/2026/05/megalodon-github-attack-targets-5561.html) |
| 2026-05-19 | @antv ecosystem (Mini Shai-Hulud) | npm | 639 malicious versions across 323 packages; 640 packages removed; 61,274 npm tokens invalidated; ~22-minute publish burst | `@antv/g@6.4.1`, `@antv/g@6.5.1`, `echarts-for-react@3.1.7`, `size-sensor@1.0.4` (full list via GitHub Advisory DB search `type:malware` for the `atool`-maintained scope) | Compromised `atool` maintainer account; **first known forged Sigstore / SLSA provenance** (worm calls Fulcio and Rekor at runtime so packages show a valid “verified” badge); `preinstall` worm that scrapes runner-process memory for secrets; C2 `t.m-kosche[.]com:443` | [Microsoft](https://www.microsoft.com/en-us/security/blog/2026/05/20/mini-shai-hulud-compromised-antv-npm-packages-enable-ci-cd-credential-theft/); [GHSA-6fr3-r6r6-h4h9](https://github.com/advisories/GHSA-6fr3-r6r6-h4h9); [Socket](https://socket.dev/blog/antv-packages-compromised); [Snyk](https://snyk.io/blog/mini-shai-hulud-antv-npm-supply-chain-attack/) |
| 2026-05-19 | Microsoft `durabletask` (TeamPCP Wave 4) | PyPI | 3 versions, ~417K monthly downloads, 35-minute publish window | `durabletask@1.4.1`, `durabletask@1.4.2`, `durabletask@1.4.3` (clean: `1.4.0`) | PyPI token stolen in an earlier GitHub breach; modified builds uploaded via twine with no matching tags/commits/CI runs; in-source dropper fetches `rope.pyz` second-stage credential stealer and worm (propagates via AWS SSM and `kubectl exec`) | [Wiz](https://www.wiz.io/blog/durabletask-teampcp-supply-chain-attack); [Snyk](https://snyk.io/blog/durabletask-pypi-supply-chain-attack/); [Endor Labs](https://www.endorlabs.com/learn/trojanized-microsoft-sdk-durabletask-1-4-1-through-1-4-3-deliver-credential-stealing-malware); [SafeDep](https://safedep.io/malicious-durabletask-pypi-supply-chain-attack/) |
| 2026-05-19 (reported; weaponized 2023-08-19) | `shopsprint/decimal` typosquat | Go modules | 1 module; ~33-month dwell time; repo removed but module still served by `proxy.golang.org` | `github.com/shopsprint/decimal@v1.3.3` | Single-letter typosquat of `github.com/shopspring/decimal`; malicious `init()` opens a DNS-TXT C2 channel to a dynamic-DNS subdomain and passes responses to `os/exec`; persists via Go module proxy caching (same persistence class as the BoltDB row) | [Socket](https://socket.dev/blog/popular-go-decimal-library-typosquat-dns-backdoor); [GBHackers](https://gbhackers.com/single-letter-go-module-typosquat/); [CyberSecurityNews](https://cybersecuritynews.com/hackers-use-single-letter-go-module-typosquat/) |

## Contextual Incidents (Unverified / Pending Verification)

The campaigns below have been mentioned in trusted feeds but lack the per-version,
multi-source citations required for the actionable-IOC table.
Treat them as situational awareness, **not** as actionable IOCs — there is no grep-able
string here, and the hardening cool-off does not specifically target them.
If you have verified package@version + dates + at least two independent references,
promote the row into the canonical table above and remove it here.

| Date (approx.) | Name | Ecosystem | What is known | What is missing |
| --- | --- | --- | --- | --- |
| 2026-05 (reported) | BufferZoneCorp sleeper modules | Go modules + RubyGems | 9 Go modules and 7 Ruby gems under `github.com/BufferZoneCorp/*`, impersonating popular libraries (`go-retryablehttp`, `go-envconfig`); two-phase “sleeper” published clean then weaponized to tamper with `GOPROXY` / `go.sum` and plant SSH keys; reported by Socket. All blocked. | Exact `module@version` strings (not publicly published); independent technical analysis beyond the single primary source. |

## How To Use This Table

- **Spot-check installed packages.** Grep lockfiles and installed trees for any
  `pkg@version` above.
  The npm hardening guide includes a ready-made grep template in `hardening-npm.md` →
  “Compromise Assessment”.
  The PyPI hardening guide includes an equivalent in `hardening-pypi.md` → “Compromise
  Assessment”.
- **Reference, do not duplicate.** Per-ecosystem hardening and research docs link to
  this table rather than reproducing it.
  New rows are added here first.
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
  The 2026-05-19 @antv worm forged valid Sigstore / SLSA attestations at runtime: a
  valid attestation confirms *which pipeline* produced a package, not that the pipeline
  was uncompromised. Treat provenance as one signal, not a guarantee; see
  [`guidelines/hardening-ci-cd.md`](guidelines/hardening-ci-cd.md).

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
