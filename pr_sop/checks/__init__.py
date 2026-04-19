"""Check registry."""

from pr_sop.checks.base import Check, Finding
from pr_sop.checks.changelog_required import ChangelogRequired
from pr_sop.checks.precommit_rev_matches import PrecommitRevMatchesTag
from pr_sop.checks.version_consistency import VersionConsistency

ALL_CHECKS: list[type[Check]] = [
    ChangelogRequired,
    VersionConsistency,
    PrecommitRevMatchesTag,
]

__all__ = [
    "ALL_CHECKS",
    "Check",
    "Finding",
    "ChangelogRequired",
    "VersionConsistency",
    "PrecommitRevMatchesTag",
]
