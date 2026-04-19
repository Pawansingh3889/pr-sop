"""Tests for config loading."""

from __future__ import annotations

from pathlib import Path

from pr_sop.config import PrSopConfig


def test_missing_file_returns_empty_config(tmp_path: Path) -> None:
    cfg = PrSopConfig.load(tmp_path / "absent.yml")
    assert cfg.checks.changelog_required is None


def test_loads_all_three_checks(tmp_path: Path) -> None:
    path = tmp_path / ".prsop.yml"
    path.write_text(
        """
checks:
  changelog_required:
    severity: error
    paths: [\"src/*.py\"]
  version_consistency:
    severity: error
    sources:
      - file: pyproject.toml
        pattern: 'version = \"([^\"]+)\"'
  precommit_rev_matches_tag:
    severity: warning
""",
        encoding="utf-8",
    )
    cfg = PrSopConfig.load(path)
    assert cfg.checks.changelog_required is not None
    assert cfg.checks.changelog_required.paths == ["src/*.py"]
    assert cfg.checks.version_consistency is not None
    assert cfg.checks.version_consistency.sources[0]["file"] == "pyproject.toml"
    assert cfg.checks.precommit_rev_matches_tag is not None


def test_empty_yaml_returns_empty_config(tmp_path: Path) -> None:
    path = tmp_path / ".prsop.yml"
    path.write_text("", encoding="utf-8")
    cfg = PrSopConfig.load(path)
    assert cfg.checks.changelog_required is None
