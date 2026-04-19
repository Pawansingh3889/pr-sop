"""Tests for version-consistency check."""

from __future__ import annotations

from pathlib import Path

from pr_sop.checks.base import CheckContext
from pr_sop.checks.version_consistency import VersionConsistency
from pr_sop.config import VersionConsistencyConfig


def _ctx(tmp_path: Path) -> CheckContext:
    return CheckContext(repo_root=tmp_path, changed_files=[])


def test_consistent_versions_pass(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('version = "1.2.3"\n', encoding="utf-8")
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text('__version__ = "1.2.3"\n', encoding="utf-8")
    cfg = VersionConsistencyConfig(
        sources=[
            {"file": "pyproject.toml", "pattern": r'version\s*=\s*"([^"]+)"'},
            {"file": "pkg/__init__.py", "pattern": r'__version__\s*=\s*"([^"]+)"'},
        ]
    )
    assert VersionConsistency(config=cfg).run(_ctx(tmp_path)) == []


def test_drift_detected(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('version = "1.2.3"\n', encoding="utf-8")
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text('__version__ = "1.2.2"\n', encoding="utf-8")
    cfg = VersionConsistencyConfig(
        sources=[
            {"file": "pyproject.toml", "pattern": r'version\s*=\s*"([^"]+)"'},
            {"file": "pkg/__init__.py", "pattern": r'__version__\s*=\s*"([^"]+)"'},
        ]
    )
    findings = VersionConsistency(config=cfg).run(_ctx(tmp_path))
    assert len(findings) == 2
    assert all("drift" in f.message.lower() for f in findings)


def test_missing_file_fires(tmp_path: Path) -> None:
    cfg = VersionConsistencyConfig(
        sources=[{"file": "missing.toml", "pattern": r"version = ([0-9.]+)"}]
    )
    findings = VersionConsistency(config=cfg).run(_ctx(tmp_path))
    assert len(findings) == 1
    assert "does not exist" in findings[0].message


def test_invalid_regex_fires(tmp_path: Path) -> None:
    (tmp_path / "f.txt").write_text("x", encoding="utf-8")
    cfg = VersionConsistencyConfig(sources=[{"file": "f.txt", "pattern": "("}])
    findings = VersionConsistency(config=cfg).run(_ctx(tmp_path))
    assert len(findings) == 1
    assert "Invalid regex" in findings[0].message


def test_pattern_no_match_fires(tmp_path: Path) -> None:
    (tmp_path / "a.toml").write_text("no version here\n", encoding="utf-8")
    cfg = VersionConsistencyConfig(
        sources=[{"file": "a.toml", "pattern": r'version = "([^"]+)"'}]
    )
    findings = VersionConsistency(config=cfg).run(_ctx(tmp_path))
    assert len(findings) == 1
    assert "did not match" in findings[0].message
