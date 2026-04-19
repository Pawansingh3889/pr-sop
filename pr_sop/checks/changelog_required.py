"""changelog-required: CHANGELOG entry required when matching paths change."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass

from pr_sop.checks.base import CheckContext, Finding
from pr_sop.config import ChangelogRequiredConfig


@dataclass
class ChangelogRequired:
    check_id: str = "changelog-required"
    config: ChangelogRequiredConfig | None = None

    def run(self, ctx: CheckContext) -> list[Finding]:
        if self.config is None or self.config.severity == "off":
            return []

        matched = [
            p for p in ctx.changed_files
            if any(fnmatch.fnmatch(p, pat) for pat in self.config.paths)
        ]
        if not matched:
            return []

        # CHANGELOG itself changing counts as satisfying the requirement.
        if self.config.changelog_file in ctx.changed_files:
            return self._check_unreleased_section(ctx)

        return [
            Finding(
                check_id=self.check_id,
                severity=self.config.severity,
                message=(
                    f"{len(matched)} file(s) matching configured paths changed, "
                    f"but {self.config.changelog_file} was not updated."
                ),
                file=self.config.changelog_file,
                suggestion=(
                    f"Add an entry under `{self.config.unreleased_heading}` in "
                    f"{self.config.changelog_file} describing this change."
                ),
            )
        ]

    def _check_unreleased_section(self, ctx: CheckContext) -> list[Finding]:
        """If CHANGELOG changed, make sure it has an [Unreleased] section with content."""
        assert self.config is not None
        path = ctx.repo_root / self.config.changelog_file
        if not path.exists():
            return []
        text = path.read_text(encoding="utf-8")
        if self.config.unreleased_heading not in text:
            return [
                Finding(
                    check_id=self.check_id,
                    severity=self.config.severity,
                    message=(
                        f"{self.config.changelog_file} is missing "
                        f"`{self.config.unreleased_heading}` section."
                    ),
                    file=self.config.changelog_file,
                    suggestion=(
                        f"Add `{self.config.unreleased_heading}` above the latest "
                        f"version heading."
                    ),
                )
            ]
        # Check there's non-whitespace content between [Unreleased] and next ## heading.
        after = text.split(self.config.unreleased_heading, 1)[1]
        # Trim to next level-2 heading.
        next_heading_idx = after.find("\n## ")
        section = after[:next_heading_idx] if next_heading_idx != -1 else after
        if not section.strip():
            return [
                Finding(
                    check_id=self.check_id,
                    severity=self.config.severity,
                    message=(
                        f"`{self.config.unreleased_heading}` section in "
                        f"{self.config.changelog_file} is empty."
                    ),
                    file=self.config.changelog_file,
                    suggestion="Add at least one bullet describing the change.",
                )
            ]
        return []
