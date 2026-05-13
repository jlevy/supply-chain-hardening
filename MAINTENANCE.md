# Maintenance

**Last updated:** 2026-05-12

**Author:** Joshua Levy (github.com/jlevy) with agent assistance

This doc tracks the package-manager versions the playbooks have been validated against,
and the procedure for re-verifying when those tools release new major versions.

## Last Verified Against

| Tool | Version | Verified date | Validator | Notes |
| --- | --- | --- | --- | --- |
| npm | 11.x | 2026-05-12 | initial author | `NPM_CONFIG_MIN_RELEASE_AGE` requires 11.10+ |
| pnpm | 10.x | 2026-05-12 | initial author | `MINIMUM_RELEASE_AGE` requires 10.16.0+; `strictDepBuilds` / `allowBuilds` per 10.26+ |
| pip | 26.1 | 2026-05-12 | initial author | `PIP_UPLOADED_PRIOR_TO` accepts ISO 8601 duration in 26.1+ |
| uv | latest | 2026-05-12 | initial author | `UV_NO_BUILD` documented; `UV_ONLY_BINARY` confirmed not a real env var |
| cargo | 1.83+ | 2026-05-12 | initial author | `cargo-vet`, `cargo-deny`, `cargo-audit` versions pinned in CI examples |
| go | 1.25.10 / 1.26.3 | 2026-05-12 | initial author | Minimum for CVE-2026-42501 fix |

## Re-Verify On Major-Version Bump

When npm, pnpm, pip, uv, Cargo, or Go publishes a major release, run the following
before bumping the corresponding row above:

1. **Read the release notes** for added / renamed / removed config options.
2. **Check the env-var documentation page** for the canonical names:
   - npm: <https://docs.npmjs.com/cli/v11/configuring-npm/npmrc>
   - pnpm: <https://pnpm.io/settings>
   - pip: <https://pip.pypa.io/en/stable/topics/configuration/>
   - uv: <https://docs.astral.sh/uv/reference/environment/>
   - cargo: <https://doc.rust-lang.org/cargo/reference/config.html>
   - go: <https://pkg.go.dev/cmd/go#hdr-Environment_variables>
3. **Update `tests/known-env-vars.txt`** if names changed.
4. **Run the validator:** `python3 tests/validate-docs.py`.
5. **Update the playbook** if a control’s flag name or unit changed.
6. **Bump the row in the Last Verified Against table** with the verifier’s name and the
   date.
7. **Open an audit-log entry** if any control changed semantics (so the change is
   visible to future readers; see
   [`supply-chain-audit-log-template.md`](supply-chain-audit-log-template.md)).

## Related

- [`self-update-instructions.md`](self-update-instructions.md) covers the procedure for
  incident / playbook / research-doc updates.
- [`tests/known-env-vars.txt`](tests/known-env-vars.txt) is the validator’s source of
  truth.
- [`.github/workflows/doc-lint.yml`](.github/workflows/doc-lint.yml) wires the validator
  into CI.

<!-- This document follows std-doc-guidelines.md.
Review guidelines before editing.
-->
