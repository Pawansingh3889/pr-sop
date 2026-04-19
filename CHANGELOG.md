# Changelog

All notable changes to **pr-sop** are logged here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
pr-sop uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.2] - 2026-04-19

### Fixed
- `precommit-rev-matches-tag` now surfaces drift in GitHub Actions PR
  runs that it silently passed before. The previous implementation
  used `git describe --tags --abbrev=0`, which requires the latest
  release tag to be an ancestor of HEAD. In Actions `pull_request`
  runs, the ephemeral merge commit GitHub creates is often not a
  descendant of the tag, so describe returned non-zero and the check
  returned an empty findings list without any indication anything had
  gone wrong. The check now uses `git tag --sort=-v:refname` and
  picks the highest version across all tags in the repo, regardless
  of reachability. That is also the right semantic: "does your
  `rev:` pin match the most recent release?" does not depend on
  branch topology. Discovered against sql-guard; the PR governance
  workflow now surfaces the expected `v0.4.0` vs `v0.4.1` drift on
  `.pre-commit-config.yaml`.

### Added
- Full project documentation pass: `CONTRIBUTING.md`, `GOVERNANCE.md`,
  `CODE_OF_CONDUCT.md`, `SECURITY.md`, and `NOTICE`, modelled on the
  sql-guard / sql-sop set. README restructured with a badges row, a
  Links block, a "Why Does This Exist?" narrative, a Key Numbers
  table, an example terminal output, and a workflow snippet pinned
  at `Pawansingh3889/pr-sop@v0.1.1`.

## [0.1.1] - 2026-04-19

### Fixed
- `precommit-rev-matches-tag` no longer fires on third-party `rev:` pins in
  `.pre-commit-config.yaml`. The check now only flags pins whose surrounding
  `repo:` URL resolves to the current repo, determined from `git remote
  get-url origin` (with a normaliser that treats HTTPS and SSH forms of the
  same `owner/name` as equal). This makes the check usable in any repo whose
  pre-commit config pulls in third-party hooks, which is effectively every
  repo. Discovered while wiring pr-sop into sql-guard.

### Added
- New `PrecommitRevMatchesTagConfig.repo_url_pattern` field (regex) to force
  the self-matching set explicitly, overriding the `origin` auto-detection.
  Useful on forks or in CI runs where `origin` points at a mirror.

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
