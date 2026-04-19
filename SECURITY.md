# Security policy

pr-sop is a PR governance tool. The primary security concerns are
**false negatives** (drift a check misses that users trust it to catch)
and **config-parsing vulnerabilities** (bad `.prsop.yml` inputs that
crash or misbehave). This document sets out how to report those and
what to expect.

## Supported versions

The latest minor version series on PyPI is supported. Older series
receive security fixes for 90 days after a newer minor ships.

| Version | Status | Support ends |
| --- | --- | --- |
| 0.1.x | current | (none yet) |

Always upgrade to the latest release before filing a bug.

## Threat model

pr-sop is a static analyser for repo metadata. It does not execute
arbitrary code, connect to external services, or send telemetry. The
surfaces that matter:

| Surface | Protection | Where |
| --- | --- | --- |
| Check coverage | Every check has fires-on-bad and does-not-fire-on-good tests | `tests/` |
| Config loading | pydantic v2 schema with strict validation | `pr_sop/config.py` |
| Git shell-outs | Fixed argv, `capture_output=True`, 5-second timeout, no shell=True | `pr_sop/checks/*.py` |
| File reads | UTF-8, explicit paths from config, no glob traversal outside repo | `pr_sop/checks/*.py` |
| PyPI releases | Manual `twine upload` today; trusted publishing planned | `pyproject.toml` |

What a report should cover:

- **False negatives**, drift that should trigger a check but does not.
  Highest priority.
- **False positives that waste user time at scale**, a check that
  fires on good state common in real repos.
- **Check bypasses via input crafting**, if you can construct a
  `.prsop.yml`, a CHANGELOG, or a rev pin that looks suspicious to a
  reader but does not trigger the relevant check.
- **Config-parsing crashes or injections**, a malformed `.prsop.yml`
  that crashes pr-sop or causes it to shell-execute unintended
  commands.
- **Supply-chain concerns**, an upstream dependency (pydantic, PyYAML,
  typer, rich) with a CVE that affects pr-sop at load or scan time.

## Reporting a vulnerability

**Do not open a public GitHub issue for a security problem.**

Report privately via the GitHub security advisory form:

<https://github.com/Pawansingh3889/pr-sop/security/advisories/new>

Include:

1. **What you found**, one-sentence description.
2. **Reproduction**, the smallest `.prsop.yml` or repo state that
   reproduces the issue, plus the expected behaviour.
3. **Check ID** involved, if any.
4. **Impact**, what kind of real-world problem could reach
   production if a user relied on pr-sop.
5. **Suggested fix**, optional. Code change, schema tightening, or a
   new test case.

## What to expect

| Severity | Initial response | Fix target |
| --- | --- | --- |
| Critical (check bypass on documented-dangerous drift) | within 48 hours | within 7 days |
| High (false positive on widespread good-state pattern, or config-parsing crash) | within 5 days | next patch release |
| Medium | within 7 days | next minor release |
| Low / info | within 14 days | when scoped |

## Coordinated disclosure

Default 90 days. Sooner if the fix has shipped to PyPI and you agree.

## Scope

**In scope:**

- Everything in `pr_sop/`
- Tests in `tests/`
- The GitHub Action entry point (`action.yml`)
- The published PyPI artefact (`pr-sop`)

**Out of scope:**

- Upstream CVEs in pydantic, PyYAML, typer, or rich (report upstream;
  link the advisory here so we can pin the fix)
- User misconfiguration of `.prsop.yml`
- Policy questions ("why isn't check X built-in?"), open a feature
  request issue instead

## Previous advisories

None.
