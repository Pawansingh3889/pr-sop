"""Engine: load config, discover changed files, run checks, collect findings."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from pr_sop.checks import ChangelogRequired, PrecommitRevMatchesTag, VersionConsistency
from pr_sop.checks.base import CheckContext, Finding
from pr_sop.config import PrSopConfig


@dataclass
class ScanResult:
    findings: list[Finding]
    checks_run: list[str]

    @property
    def error_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "warning")

    @property
    def exit_code(self) -> int:
        return 1 if self.error_count > 0 else 0


def changed_files(repo_root: Path, base_ref: str | None) -> list[str]:
    """Return paths changed vs base_ref. If base_ref is None, return all tracked files."""
    if base_ref:
        cmd = ["git", "diff", "--name-only", f"{base_ref}...HEAD"]
    else:
        cmd = ["git", "ls-files"]
    try:
        result = subprocess.run(
            cmd, cwd=repo_root, capture_output=True, text=True, timeout=10
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return []
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line]


def run_scan(repo_root: Path, config: PrSopConfig, base_ref: str | None) -> ScanResult:
    files = changed_files(repo_root, base_ref)
    ctx = CheckContext(repo_root=repo_root, changed_files=files)

    findings: list[Finding] = []
    checks_run: list[str] = []

    if config.checks.changelog_required:
        check = ChangelogRequired(config=config.checks.changelog_required)
        checks_run.append(check.check_id)
        findings.extend(check.run(ctx))

    if config.checks.version_consistency:
        check = VersionConsistency(config=config.checks.version_consistency)
        checks_run.append(check.check_id)
        findings.extend(check.run(ctx))

    if config.checks.precommit_rev_matches_tag:
        check = PrecommitRevMatchesTag(config=config.checks.precommit_rev_matches_tag)
        checks_run.append(check.check_id)
        findings.extend(check.run(ctx))

    return ScanResult(findings=findings, checks_run=checks_run)
