# Changelog

All notable changes to **pr-sop** are logged here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
pr-sop uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-04-19

### Added
- First release. Three opinionated checks you wire up with a YAML block:
  - `changelog-required` — flag PRs that change configured paths without
    touching `CHANGELOG.md`, or that leave `## [Unreleased]` empty.
  - `version-consistency` — extract version strings from N configured
    files via regex, fail on drift. Catches the classic "bumped
    `pyproject.toml`, forgot the `__init__.py`" mistake.
  - `precommit-rev-matches-tag` — warn when `rev:` pins in README or
    `.pre-commit-hooks.yaml` don't match the latest git tag.
- CLI (`pr-sop check`) with Rich terminal output.
- GitHub Action (`action.yml`) emitting `::error::` / `::warning::`
  workflow commands plus a `$GITHUB_STEP_SUMMARY` table. No PyGithub
  dependency, no token setup beyond default `GITHUB_TOKEN`.
- Pydantic v2 config schema. Typos in `.prsop.yml` fail fast at load.
- Dogfooded against this repo via `.prsop.yml`.
- Validated end-to-end against sql-sop: clean on HEAD, catches three
  real drift issues on the pre-cleanup commit (version mismatch,
  stale `rev:` pin).
