# pr-sop

[![PyPI](https://img.shields.io/pypi/v/pr-sop)](https://pypi.org/project/pr-sop/)
[![Python](https://img.shields.io/pypi/pyversions/pr-sop)](https://pypi.org/project/pr-sop/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/pr-sop?color=a07aff)](https://pypi.org/project/pr-sop/)

Opinionated PR governance checks. Config-driven, no LLM. Runs as a CLI,
pre-commit hook, or GitHub Action.

Built by the author of [sql-sop](https://github.com/Pawansingh3889/sql-guard).
Same naming, same philosophy: catch real drift fast, skip the ceremony.

## Links
- [GitHub](https://github.com/Pawansingh3889/pr-sop)
- [PyPI](https://pypi.org/project/pr-sop/)
- [Download stats](https://pypistats.org/packages/pr-sop)
- Install: `pip install pr-sop`
- [Profile](https://github.com/Pawansingh3889)
- **Contributing:** [`CONTRIBUTING.md`](CONTRIBUTING.md) · [`GOVERNANCE.md`](GOVERNANCE.md) · [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) · [`SECURITY.md`](SECURITY.md) · [`NOTICE`](NOTICE)

## Why Does This Exist?

Teams keep shipping PRs with broken `CHANGELOG.md`, `pyproject.toml` versions that do not match the `__init__.py`, or `rev:` pins in READMEs that still point at a tag three releases behind. Every repo hits these. Every review catches some and misses others.

pr-sop is a tiny, config-driven checker that runs before merge and surfaces the drift that review forgets. No LLM, no opinions beyond what you turn on in `.prsop.yml`. Three checks today, each optional, each under 100 lines.

### Key Numbers

| | |
|---|---|
| Checks | 3 (2 errors, 1 warning) |
| Tests | 29 |
| Runtime | under 1 second on a typical PR |
| Version | 0.1.1 |

## What it checks

| ID | Default severity | What it catches |
| --- | --- | --- |
| `changelog-required` | error | Files matching a glob pattern changed, but `CHANGELOG.md` was not updated, or the `## [Unreleased]` section is missing or empty. |
| `version-consistency` | error | Version strings extracted from multiple files disagree. Catches the classic "bumped pyproject, forgot the `__init__.py`" drift. |
| `precommit-rev-matches-tag` | warning | `rev:` pins in configured files (README, pre-commit config) do not match the latest git tag. Since v0.1.1, only pins referencing this repo are flagged, so third-party hooks are ignored automatically. |

Every check is optional and configured in `.prsop.yml`. A missing section means the check is off.

## Quick start

```bash
pip install pr-sop
```

Drop a `.prsop.yml` at the repo root:

```yaml
checks:
  changelog_required:
    severity: error
    paths:
      - "src/**/*.py"

  version_consistency:
    severity: error
    sources:
      - file: pyproject.toml
        pattern: '^version\s*=\s*"([^"]+)"'
      - file: src/mypkg/__init__.py
        pattern: '^__version__\s*=\s*"([^"]+)"'

  precommit_rev_matches_tag:
    severity: warning
    files:
      - README.md
      - .pre-commit-config.yaml
```

Run:

```bash
pr-sop check --base origin/main
```

Exit code is `1` if any `error` fired, `0` otherwise. Warnings never fail CI.

Example terminal output:

```
ERROR    changelog-required  src/myapp/api.py  3 changed paths match but CHANGELOG.md was not updated.
       -> Add a line under `## [Unreleased]` in CHANGELOG.md.
WARNING  precommit-rev-matches-tag  README.md:134  `rev: v0.3.2` does not match latest git tag `v0.4.1`.
       -> Update the rev to `v0.4.1`.

1 error(s), 1 warning(s) across 2 check(s).
```

## GitHub Action

```yaml
name: pr-sop
on:
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  prsop:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          fetch-tags: true

      - uses: Pawansingh3889/pr-sop@v0.1.1
```

Findings surface as native `::error::` and `::warning::` workflow commands (visible in the Files tab of the PR) plus a table in the workflow summary. No API calls, no token setup beyond the default `GITHUB_TOKEN`.

Consumer inputs on the action:

| Input | Default | Description |
| --- | --- | --- |
| `config` | `.prsop.yml` | Path to the config file relative to the repo root. |
| `base` | auto | Base ref to diff against. Empty defaults to the PR base, or `origin/main` otherwise. |

## Why not Danger?

Danger is great when you want to write repo-specific rules in JavaScript.
pr-sop is the opposite: three opinionated rules you turn on with a YAML block,
no Dangerfile to maintain. If you need custom logic, reach for Danger. If you
keep forgetting to bump the CHANGELOG, reach for pr-sop.

## Design

- Checks are plugins (see [`pr_sop/checks/base.py`](pr_sop/checks/base.py)). Each has an id, a pydantic config model, and a `run(ctx) -> list[Finding]`.
- No network calls. Reads your files, shells out to `git`.
- Config validated by pydantic v2. Typos in `.prsop.yml` fail fast at load, not mid-scan.
- Output: Rich terminal locally, workflow commands in Actions.
- Single source of version truth via `importlib.metadata`, no hardcoded version string to drift.

## Used by

- [sql-guard](https://github.com/Pawansingh3889/sql-guard) (aka `sql-sop` on PyPI), as the first external consumer since v0.1.0.

If you wire pr-sop into your repo and want to be listed, open a PR adding a bullet here.

## Status

v0.1.1, alpha. The config schema and rule IDs are the parts most likely to stay stable across 0.x. Internal APIs in `pr_sop/checks/` may move before v1.0. Check `CHANGELOG.md` before upgrading between minor versions.

## Licence

MIT. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE) for the reasoning.
