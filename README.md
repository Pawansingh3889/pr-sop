# pr-sop

Opinionated PR governance checks. Config-driven, no LLM. Runs as a CLI,
pre-commit hook, or GitHub Action.

Built by the author of [sql-sop](https://github.com/Pawansingh3889/sql-guard).
Same naming, same philosophy: catch real drift fast, skip the ceremony.

## What it checks (v0.1)

| ID | Default severity | What it catches |
| --- | --- | --- |
| `changelog-required` | error | Files matching a glob pattern changed, but `CHANGELOG.md` wasn't updated, or the `## [Unreleased]` section is missing/empty. |
| `version-consistency` | error | Version strings extracted from multiple files disagree. Catches the classic "bumped pyproject, forgot the `__init__.py`" drift. |
| `precommit-rev-matches-tag` | warning | `rev:` pins in README or `.pre-commit-hooks.yaml` don't match the latest git tag. |

Every check is optional and configured in `.prsop.yml`. Missing section means
the check is off.

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
      - .pre-commit-hooks.yaml
```

Run:

```bash
pr-sop check --base origin/main
```

Exit code is `1` if any `error` fired, `0` otherwise. Warnings never fail CI.

## GitHub Action

```yaml
- uses: Pawansingh3889/pr-sop@v0.1.0
```

Findings surface as native check-run annotations in the PR Files tab plus a
table in the workflow summary. No API calls, no token setup beyond the default
`GITHUB_TOKEN`.

## Why not Danger?

Danger is great when you want to write repo-specific rules in JavaScript.
pr-sop is the opposite: three opinionated rules you turn on with a YAML block,
no Dangerfile to maintain. If you need custom logic, use Danger. If you keep
forgetting to bump the changelog, use pr-sop.

## Design

- Checks are plugins (see `pr_sop/checks/base.py`). Each has an id, a config
  model, and a `run(ctx) -> list[Finding]`.
- No network calls. Reads your files, shells out to `git`.
- Config validated by pydantic v2. Typos fail fast, not mid-scan.
- Output: Rich terminal locally, workflow commands in Actions.

## Status

v0.1.0, alpha. API will stabilise at v1.0.

## Licence

MIT.
