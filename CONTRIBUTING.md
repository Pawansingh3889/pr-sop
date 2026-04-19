# Contributing to pr-sop

pr-sop is a tiny, config-driven PR governance tool published on PyPI.
Contributions are welcome; the rules below keep the project fast, stable,
and trustworthy to downstream users.

Before you start, skim:

- [**`GOVERNANCE.md`**](GOVERNANCE.md), roles, first-PR-wins, why the
  licence will stay MIT.
- [**`CODE_OF_CONDUCT.md`**](CODE_OF_CONDUCT.md), behavioural bar.
- [**`SECURITY.md`**](SECURITY.md), false-negative / bypass reports go
  there, not in a public issue.

## The Prime Directive

**Every check has tests that cover both "fires on bad state" and "does
not fire on good state".** Check IDs (`changelog-required`, `version-consistency`,
`precommit-rev-matches-tag`) and config-field names are **public API**. They
appear in downstream users' `.prsop.yml` files and CI configs. Do not
renumber, do not silently change default severity, do not remove without a
deprecation window.

## Quick Start

```bash
git clone https://github.com/Pawansingh3889/pr-sop.git
cd pr-sop
pip install -e ".[dev]"
pytest -q        # 29 tests across all checks + config
ruff check .
```

Try the CLI locally against this repo:

```bash
pr-sop check --repo . --config .prsop.yml --base origin/main
```

## How to Contribute

1. **Find or open an issue.** Watch labels `good first issue`,
   `help wanted`, `new-check`.
2. **Claim it** by commenting, 7-day soft claim per `GOVERNANCE.md`.
3. **Branch.** `feat/<short-name>`, `fix/<short-name>`, or
   `docs/<short-name>`.
4. **Code plus tests.**
5. **Before pushing:** `ruff check .`, `pytest -q`.
6. **Open the PR.** Conventional commit style, one logical change per
   commit.

## Adding a new check

The common case. Walkthrough:

1. Pick a `check_id` in kebab-case that reads like an assertion the
   tool is making (for example `changelog-required`, not `check-changelog`).
2. Add a new file under `pr_sop/checks/` with a dataclass implementing
   the `Check` protocol (see [`pr_sop/checks/base.py`](pr_sop/checks/base.py)).
3. Add a pydantic config model to `pr_sop/config.py` and wire it into
   `ChecksConfig`.
4. Add the check to the engine registry in `pr_sop/engine.py`.
5. Write tests in `tests/test_<check_id>.py`:
   - one "fires on bad state" case
   - one "does NOT fire on good state" case
   - edge cases specific to the check (missing files, empty config, etc.)
6. Update `CHANGELOG.md` under `[Unreleased]`, the "What it checks"
   table in `README.md`, and the Key Numbers count.

Check naming conventions:

- kebab-case, assertion-oriented (`changelog-required`, not
  `check-changelog` or `checkChangelog`)
- `Finding.message` tells the user what is wrong in one line
- `Finding.suggestion` tells them what to do instead

## Code Standards

- Python 3.10+.
- Line length 100.
- Type hints on public API.
- Every check class has a docstring citing the drift it catches.
- No network calls from checks. Reads files, shells out to `git`.

## Removing or renaming a check

This is a breaking change for downstream `.prsop.yml` users. Process:

1. Open an issue naming the check, the reason for removal, and the
   deprecation window (one minor version minimum).
2. Land a warning in the check's output pointing at the replacement.
3. After the deprecation window, the removal lands in a new minor
   version with the change in `CHANGELOG.md` and `README.md`.

## Reporting bugs

Open an issue with:

- Exact input that triggers or fails to trigger the check (a minimal
  repo or a concrete example in the issue body)
- Check ID involved
- pr-sop version (`pr-sop --version`)
- Python version, OS

## Feature requests

Open an issue describing:

- What drift pattern should be caught (or stop being caught)
- Why it is dangerous or why the current behaviour is noisy
- Examples of the pattern in real repos

## Recognition

Merged PRs land in the git history permanently. The README credits
substantial contributors when appropriate.
