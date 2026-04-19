"""version-consistency: configured files must all report the same version."""

from __future__ import annotations

import re
from dataclasses import dataclass

from pr_sop.checks.base import CheckContext, Finding
from pr_sop.config import VersionConsistencyConfig


@dataclass
class VersionConsistency:
    check_id: str = "version-consistency"
    config: VersionConsistencyConfig | None = None

    def run(self, ctx: CheckContext) -> list[Finding]:
        if self.config is None or self.config.severity == "off":
            return []
        if not self.config.sources:
            return []

        extracted: dict[str, tuple[str, int]] = {}  # file -> (version, line)
        findings: list[Finding] = []

        for source in self.config.sources:
            file_rel = source.get("file", "")
            pattern = source.get("pattern", "")
            if not file_rel or not pattern:
                continue

            path = ctx.repo_root / file_rel
            if not path.exists():
                findings.append(
                    Finding(
                        check_id=self.check_id,
                        severity=self.config.severity,
                        message=f"Configured source file does not exist: {file_rel}",
                        file=file_rel,
                    )
                )
                continue

            try:
                rx = re.compile(pattern)
            except re.error as e:
                findings.append(
                    Finding(
                        check_id=self.check_id,
                        severity=self.config.severity,
                        message=f"Invalid regex for {file_rel}: {e}",
                        file=file_rel,
                    )
                )
                continue

            found = None
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                m = rx.search(line)
                if m and m.groups():
                    found = (m.group(1), lineno)
                    break

            if found is None:
                findings.append(
                    Finding(
                        check_id=self.check_id,
                        severity=self.config.severity,
                        message=f"Pattern did not match any line in {file_rel}.",
                        file=file_rel,
                        suggestion="Check the `pattern` regex in .prsop.yml.",
                    )
                )
            else:
                extracted[file_rel] = found

        if len(extracted) < 2:
            return findings

        versions = {v for v, _ in extracted.values()}
        if len(versions) > 1:
            summary = ", ".join(f"{f}={v!r}" for f, (v, _) in extracted.items())
            for file_rel, (v, lineno) in extracted.items():
                findings.append(
                    Finding(
                        check_id=self.check_id,
                        severity=self.config.severity,
                        message=f"Version drift across sources. Found: {summary}",
                        file=file_rel,
                        line=lineno,
                        suggestion="Align every source to the same version string.",
                    )
                )

        return findings
