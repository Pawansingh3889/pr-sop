# pr-sop governance

A small, focused PR governance tool published on PyPI. Governance matches
the project's scope, short, explicit about the PyPI-stability bar.

## Roles

### Maintainer

Currently: **[@Pawansingh3889](https://github.com/Pawansingh3889)**.

Final decision on:

- merges to `main`
- PyPI releases
- check additions / removals
- the licence (see `NOTICE` for why MIT is deliberately kept)
- this governance document

Commits to:

- replying to issues and PRs within **7 calendar days**
- merging green, in-scope PRs within **14 calendar days**
- batching PyPI releases so downstream users do not see a new
  version every week

### Triage collaborator

Granted to contributors with three merged, in-scope PRs. Can label,
assign, and close duplicate or off-topic issues. Cannot merge, publish
to PyPI, or change repository settings.

### Contributor

Anyone who files an issue or opens a PR.

## Decisions

Check additions and check tightenings, one maintainer approval on the
PR. Every new check needs a test covering both "fires on bad state" and
"does not fire on good state".

Check removals, check ID renames, default-severity changes, config-field
removals, start as an **issue with a proposal**, because these break
downstream `.prsop.yml` files. Proposal template:

1. why the check or field is being removed or changed
2. what replaces it (if anything)
3. a deprecation window, usually one minor version

### Architecture Decision Records (ADRs)

Proposals that change *how* pr-sop works (new execution model,
new distribution format, new reporter backend) are labelled **`ADR`**
on the issue so they stay easy to find later. After discussion lands
on a decision, a follow-up issue with the task breakdown references
back to the ADR, and the ADR issue stays open in an archived state as
the record of "why we did it this way."

## Issue assignment (first-PR-wins)

1. Comment "I would like to work on this", 7-day soft claim.
2. Expires silently after 7 days; anyone may pick up.
3. If two PRs land, the first to pass CI and request review wins.

## Scope discipline

Hard lines:

- **Rule-based, not AI.** pr-sop stays a pure-Python checker that reads
  your files and shells out to `git`. No LLM, no network calls from
  checks, no telemetry.
- **Low false-positive rate.** A check that fires on good state costs
  every downstream user minutes of triage. Prefer "stay silent" to
  "fire and suggest".
- **Stable check IDs and config fields.** `changelog-required`,
  `precommit_rev_matches_tag.files`, and similar names are public API.
  Do not renumber or rename without the deprecation process.
- **Tests per check.** No check lands without at least one "fires on
  bad state" test and one "does not fire on good state" test.
- **No scope creep into code review.** pr-sop checks metadata drift
  (CHANGELOG, versions, rev pins), not code quality. For code-level
  review, reach for linters, Danger, or a human.

## Release cadence

Batched releases to PyPI via the trusted-publishing workflow (planned for
a future release). Target cadence: monthly if there are changes, otherwise
when justified.

- SemVer: major.minor.patch
- Breaking changes (check removal, severity change, config-field
  removal) bump the minor version and come with one minor of
  deprecation notice
- Stable check additions bump the minor version
- Bug fixes bump the patch version

`README.md` carries a "Key Numbers" block with the current version and
count; keep that honest.

## Licensing

MIT, deliberately. See `NOTICE` for the reasoning; relicensing a
published PyPI package is a breaking change for downstream users
configured around a specific licence, so any relicense conversation is
a major-version (v1.0) event with an explicit migration notice.

## Security

See `SECURITY.md`. Security issues route via private advisory.

## Changes to this document

Via PR from the maintainer. Community input welcome in issues.
