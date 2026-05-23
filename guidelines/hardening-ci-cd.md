# CI/CD And Publish-Pipeline Hardening

**Last updated:** 2026-05-23

**Author:** Joshua Levy (github.com/jlevy) with agent assistance

The per-ecosystem playbooks ([npm](hardening-npm.md), [PyPI](hardening-pypi.md),
[crates](hardening-crates.md), [Go](hardening-go.md)) harden the **install** side: they
stop a developer or CI job from pulling a freshly-published malicious version.
This guide hardens the **publish** side: the GitHub Actions and release-pipeline
controls that stop an attacker from turning *your* repo into the thing that publishes
malware.

It is cross-ecosystem on purpose.
The dominant 2026 incidents (TanStack, the @antv Mini Shai-Hulud worm, Megalodon,
`durabletask`, `@bitwarden/cli`) never phished a maintainer password.
They compromised the CI/CD pipeline, stole a short-lived token or poisoned a build, and
published from the legitimate identity, sometimes with a valid provenance attestation
attached.
See [`../compromised-packages.md`](../compromised-packages.md) for the incident
table.

## Why The Install-Side Controls Are Not Enough Here

Release-age delay, `ignore-scripts`, and a frozen lockfile protect *consumers* of a
package. They do nothing for the *publisher*. If your release workflow can be tricked
into running attacker code, or your publish token can be read out of runner memory, the
malicious version ships under your name and is signed by your pipeline.
Consumers who trust your provenance then install it.

The kill chain in these incidents:

1. **Get code execution in CI.** A `pull_request_target` “pwn request”, a poisoned
   Actions cache, a hijacked action tag, or a sleeper dependency.
2. **Steal a credential from the runner.** OIDC tokens and “masked” secrets sit in the
   `Runner.Worker` process memory in plaintext; secret masking only redacts logs.
   The TanStack and @antv payloads read `/proc/<pid>/mem` directly.
3. **Publish from the legitimate identity,** sometimes minting valid Sigstore/SLSA
   provenance, then self-propagate to every package the stolen token can reach.

Each control below breaks one of those links.

## Control 1: Lock Down PR-Triggered Workflows

`pull_request_target` runs with the base repo’s secrets in scope while checking out
untrusted fork code.
It is the single most exploited GitHub Actions primitive.

- **Prefer `pull_request`.** It runs in the fork’s context with no access to base-repo
  secrets. Switch to it wherever you do not genuinely need secrets on PRs.

- **If you must use `pull_request_target`, never check out or execute PR head code**
  (`github.event.pull_request.head.sha`). Split the work: build/test untrusted code in a
  `pull_request` workflow with no secrets, then do any privileged post-processing in a
  separate `workflow_run` workflow that reads only the produced artifacts.

- **Never interpolate untrusted input directly into `run:`.** Assign it to an env var
  first so it cannot break out of the shell:

  ```yaml
  # WRONG: attacker-controlled title is injected into the shell
  #   run: echo "${{ github.event.pull_request.title }}"
  env:
    TITLE: ${{ github.event.pull_request.title }}
  run: echo "$TITLE"
  ```

Reference:
[GitHub Security Lab, Preventing pwn requests](https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/).

## Control 2: Make The Actions Cache Read-Only On PRs

The TanStack compromise poisoned the shared Actions cache from a `pull_request_target`
run, then a later release workflow on `main` restored the poisoned entry.
Cache *writes* use an internal runner token, not `GITHUB_TOKEN`, so a `permissions:`
block does **not** prevent them.

- In any `pull_request` / `pull_request_target` workflow, restore but never save:

  ```yaml
  # PR workflows: read-only cache
  - uses: actions/cache/restore@<full-40-char-commit-sha>  # v4
    with:
      key: pr-${{ hashFiles('pnpm-lock.yaml') }}
  ```

- Allow cache **writes** only in workflows triggered by push to a protected branch, and
  use a distinct key prefix (`release-` vs `pr-`) so the two namespaces cannot collide.

Reference:
[SafeDep, TanStack cache-poisoning postmortem](https://safedep.io/tanstack-github-actions-cache-poisoning/).

## Control 3: Set `permissions:` To Read-Only By Default

```yaml
# Top of every workflow file
permissions:
  contents: read
```

Grant write scopes (`contents: write`, `id-token: write`, `packages: write`) only on the
specific job that needs them.
Enforce the default org-wide at **Organization Settings -> Actions -> General ->
Workflow permissions -> “Read repository contents and packages permissions”**.

Reference:
[GitHub docs, Controlling permissions for GITHUB_TOKEN](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/controlling-permissions-for-github_token).

## Control 4: Pin Actions To A Commit SHA, Not A Tag

Tags are mutable. The `tj-actions/changed-files` (2025) and `trivy-action` (2026)
compromises moved a tag to point at malicious code; everyone tracking the tag pulled it
on the next run. The Trivy tag hijack is the root cause of the LiteLLM and CanisterWorm
incidents in the table.

```yaml
# Pin the full 40-character commit SHA; keep the human-readable version in a comment.
- uses: actions/checkout@<full-40-char-commit-sha>  # v4.2.2
```

Let Dependabot or Renovate propose SHA bumps so updates are reviewable diffs.
Apply this to transitive actions (actions called by your actions) too.

## Control 5: Harden The Runner (Egress Block + No Privilege Escalation)

The payloads in these incidents exfiltrated over arbitrary egress and escalated via
`sudo` / Docker.
StepSecurity Harden-Runner installs eBPF hooks before your steps run and
enforces an egress allowlist:

```yaml
- name: Harden the runner
  uses: step-security/harden-runner@<full-40-char-commit-sha>  # v2.13.0
  with:
    egress-policy: block
    disable-sudo-and-containers: true
    allowed-endpoints: >
      github.com:443
      api.github.com:443
      registry.npmjs.org:443
```

Use `disable-sudo-and-containers` (Harden-Runner v2.12.0+), not the older
`disable-sudo: true`: the sudo-only policy was bypassable via Docker group membership
(GHSA-mxr3-8whj-j74r). On self-hosted runners, install the agent in the runner image.

References:
[step-security/harden-runner](https://github.com/step-security/harden-runner);
[StepSecurity, evolving the disable-sudo policy](https://www.stepsecurity.io/blog/evolving-harden-runners-disable-sudo-policy-for-improved-runner-security).

## Control 6: Eliminate Long-Lived Publish Tokens

A stolen publish token is what the worms self-propagate with.
Remove the standing token.

- **Use OIDC Trusted Publishing.** npm Trusted Publishing (GA July 2025; requires npm

  > = 11.5.1 and Node >= 22.14.0) and PyPI Trusted Publishers mint a short-lived,
  > workflow-scoped credential per run.
  > No `NODE_AUTH_TOKEN` / API token is stored.

  ```yaml
  permissions:
    contents: read
    id-token: write
  steps:
    - uses: actions/checkout@<full-40-char-commit-sha>      # v4
    - uses: actions/setup-node@<full-40-char-commit-sha>    # v4
      with:
        node-version: "22"
        registry-url: "https://registry.npmjs.org"
    - run: npm publish --provenance --access public
  ```

- **Gate the publish behind a GitHub Environment with required reviewers** and “Prevent
  self-reviews” enabled, so even an OIDC-authenticated run waits for human approval.

- **If you must keep a token, make it granular** (npm removed legacy account-wide tokens
  in November 2025): scope it to a single package, set an expiry, and keep
  `bypass-2fa: false`.

- **Turn on npm staged publishing** (GA 2026-05-20; npm CLI >= 11.15.0).
  `npm stage publish` submits to a staging area from CI without 2FA; a maintainer must
  `npm stage approve` with 2FA before it goes live, so a stolen CI token alone cannot
  ship a release.

References: [npm Trusted publishers](https://docs.npmjs.com/trusted-publishers/);
[npm Staged publishing](https://docs.npmjs.com/staged-publishing/);
[GitHub changelog, staged publishing + install-time controls](https://github.blog/changelog/2026-05-22-staged-publishing-and-new-install-time-controls-for-npm/).

## Control 7: Treat Provenance As A Signal, Not Proof

The 2026-05-19 @antv worm was the first to forge valid Sigstore / SLSA provenance: it
called Fulcio and Rekor at runtime, so infected packages displayed a green “verified”
badge. A valid attestation confirms *which pipeline* produced the artifact, not that the
pipeline was uncompromised.

- **Verify provenance, but do not stop there.** `npm audit signatures` (npm >= 9.5.0)
  checks registry signatures and attestations.
  It is a post-install check, not an install-time gate, so run it in CI after `npm ci`
  and locally after installs.

- **Monitor the transparency log for your own identities.** The
  [`sigstore/rekor-monitor`](https://github.com/sigstore/rekor-monitor) reusable
  workflow files an issue when a Fulcio certificate is issued under a CI identity you
  did not expect, catching a forged or stolen-identity publish:

  ```yaml
  name: Rekor log monitor
  on:
    schedule:
      - cron: "0 * * * *"
  permissions: read-all
  jobs:
    monitor:
      permissions:
        contents: read
        issues: write
        id-token: write
      uses: sigstore/rekor-monitor/.github/workflows/reusable_monitoring.yml@<full-40-char-commit-sha>
      with:
        file_issue: true
  ```

References:
[OpenSSF, catching malicious package releases via a transparency log](https://openssf.org/blog/2025/12/19/catching-malicious-package-releases-using-a-transparency-log/);
[npm, verifying registry signatures](https://docs.npmjs.com/verifying-registry-signatures/).

## Control 8: Org-Level Controls

These need org or enterprise admin and protect every repo at once.

- **Require approval for fork PR workflows.** Organization Settings -> Actions ->
  General -> “Fork pull request workflows from outside collaborators” -> **“Require
  approval for all outside collaborators”**. Automated bots now scan public repos for
  exploitable `pull_request_target` patterns; manual approval blocks the drive-by.
- **Disable repo-level self-hosted runners** at the enterprise/org level, or require
  ephemeral (`--ephemeral`) / just-in-time runners.
  Shai-Hulud registered a persistent self-hosted runner (named `SHA1HULUD`) for
  re-entry; ephemeral runners deregister after one job.
- **Adopt immutable OIDC subject claims.** As of 2026-04-23 GitHub embeds immutable
  owner and repository IDs in the OIDC `sub` claim, so a recycled org/repo name cannot
  mint a token matching an old cloud trust policy.
  Auto-enabled for repos created after 2026-06-18; opt in existing repos via the REST
  API and tighten cloud trust policies to the ID-based subject.

References:
[GitHub docs, approving runs from forks](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/approve-runs-from-forks);
[GitHub changelog, immutable subject claims](https://github.blog/changelog/2026-04-23-immutable-subject-claims-for-github-actions-oidc-tokens/).

## Verification Checklist

- [ ] Every workflow file has a top-level `permissions: contents: read`; write scopes
  are per-job.
- [ ] No `pull_request_target` workflow checks out or runs PR head code.
- [ ] PR-triggered workflows use `actions/cache/restore` (read-only) with a `pr-` key
  prefix; cache saves happen only on protected-branch pushes.
- [ ] All `uses:` references are pinned to 40-character commit SHAs with a version
  comment.
- [ ] Publish workflows use OIDC Trusted Publishing (no stored token), behind an
  Environment with required reviewers; staged publishing is enabled where supported.
- [ ] Any remaining tokens are granular, scoped to one package, and expiring.
- [ ] `harden-runner` runs first in privileged jobs with `egress-policy: block` and
  `disable-sudo-and-containers: true`.
- [ ] `rekor-monitor` watches your publishing identities; `npm audit signatures` runs in
  CI.
- [ ] Org settings: fork-PR approval required, repo-level self-hosted runners disabled,
  immutable OIDC subject claims enabled.

## Sources

- [GitHub Security Lab: Preventing pwn requests](https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/)
- [GitHub docs: Controlling permissions for GITHUB_TOKEN](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/controlling-permissions-for-github_token)
- [SafeDep: TanStack GitHub Actions cache poisoning](https://safedep.io/tanstack-github-actions-cache-poisoning/)
- [step-security/harden-runner](https://github.com/step-security/harden-runner)
- [GHSA-mxr3-8whj-j74r: Harden-Runner disable-sudo bypass](https://github.com/advisories/GHSA-mxr3-8whj-j74r)
- [npm: Trusted publishers](https://docs.npmjs.com/trusted-publishers/)
- [npm: Staged publishing](https://docs.npmjs.com/staged-publishing/)
- [GitHub changelog: staged publishing and new install-time controls for npm](https://github.blog/changelog/2026-05-22-staged-publishing-and-new-install-time-controls-for-npm/)
- [OpenSSF: Catching malicious package releases using a transparency log](https://openssf.org/blog/2025/12/19/catching-malicious-package-releases-using-a-transparency-log/)
- [sigstore/rekor-monitor](https://github.com/sigstore/rekor-monitor)
- [GitHub changelog: immutable subject claims for OIDC tokens](https://github.blog/changelog/2026-04-23-immutable-subject-claims-for-github-actions-oidc-tokens/)
- [Microsoft Security: Mini Shai-Hulud, compromised @antv npm packages](https://www.microsoft.com/en-us/security/blog/2026/05/20/mini-shai-hulud-compromised-antv-npm-packages-enable-ci-cd-credential-theft/)
- [TanStack postmortem](https://tanstack.com/blog/npm-supply-chain-compromise-postmortem)

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
