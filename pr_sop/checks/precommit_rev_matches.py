"""precommit-rev-matches-tag: `rev:` pins in configured files must match latest git tag."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass

from pr_sop.checks.base import CheckContext, Finding
from pr_sop.config import PrecommitRevMatchesTagConfig


@dataclass
class PrecommitRevMatchesTag:
    check_id: str = "precommit-rev-matches-tag"
    config: PrecommitRevMatchesTagConfig | None = None

    def run(self, ctx: CheckContext) -> list[Finding]:
        if self.config is None or self.config.severity == "off":
            return []

        latest_tag = self._latest_tag(ctx.repo_root)
        if not latest_tag:
            return []

        findings: list[Finding] = []
        rev_line = re.compile(r"rev:\s*['\"]?([^'\"\s]+)['\"]?")

        for file_rel in self.config.files:
            path = ctx.repo_root / file_rel
            if not path.exists():
                continue
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                m = rev_line.search(line)
                if not m:
                    continue
                rev = m.group(1)
                if rev != latest_tag:
                    findings.append(
                        Finding(
                            check_id=self.check_id,
                            severity=self.config.severity,
                            message=(
                                f"`rev: {rev}` does not match latest git tag "
                                f"`{latest_tag}`."
                            ),
                            file=file_rel,
                            line=lineno,
                            suggestion=f"Update the rev to `{latest_tag}`.",
                        )
                    )

        return findings

    @staticmethod
    def _latest_tag(repo_root) -> str | None:
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            return None
        if result.returncode != 0:
            return None
        return result.stdout.strip() or None
