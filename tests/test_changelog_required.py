"""Tests for changelog-required check."""

from __future__ import annotations

from pathlib import Path

from pr_sop.checks.base import CheckContext
from pr_sop.checks.changelog_required import ChangelogRequired
from pr_sop.config import ChangelogRequiredConfig


def _ctx(tmp_path: Path, changed: list[str]) -> CheckContext:
    return CheckContext(repo_root=tmp_path, changed_files=changed)


def test_no_matching_paths_no_finding(tmp_path: Path) -> None:
    check = ChangelogRequired(config=ChangelogRequiredConfig(paths=["src/**/*.py"]))
    assert check.run(_ctx(tmp_path, ["docs/readme.md"])) == []


def test_matching_path_without_changelog_fires(tmp_path: Path) -> None:
    check = ChangelogRequired(config=ChangelogRequiredConfig(paths=["src/*.py"]))
    findings = check.run(_ctx(tmp_path, ["src/foo.py"]))
    assert len(findings) == 1
    assert findings[0].severity == "error"


def test_changelog_changed_with_unreleased_section_passes(tmp_path: Path) -> None:
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [Unreleased]\n\n- something changed\n\n## [0.1.0]\n",
        encoding="utf-8",
    )
    check = ChangelogRequired(config=ChangelogRequiredConfig(paths=["src/*.py"]))
    assert check.run(_ctx(tmp_path, ["src/foo.py", "CHANGELOG.md"])) == []


def test_changelog_changed_but_unreleased_empty_fires(tmp_path: Path) -> None:
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [Unreleased]\n\n## [0.1.0]\n- released\n",
        encoding="utf-8",
    )
    check = ChangelogRequired(config=ChangelogRequiredConfig(paths=["src/*.py"]))
    findings = check.run(_ctx(tmp_path, ["src/foo.py", "CHANGELOG.md"]))
    assert len(findings) == 1
    assert "empty" in findings[0].message.lower()


def test_severity_off_skips(tmp_path: Path) -> None:
    check = ChangelogRequired(
        config=ChangelogRequiredConfig(severity="off", paths=["src/*.py"])
    )
    assert check.run(_ctx(tmp_path, ["src/foo.py"])) == []
