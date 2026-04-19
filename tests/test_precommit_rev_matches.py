"""Tests for precommit-rev-matches-tag check."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from pr_sop.checks.base import CheckContext
from pr_sop.checks.precommit_rev_matches import PrecommitRevMatchesTag
from pr_sop.config import PrecommitRevMatchesTagConfig


def _init_git_with_tag(path: Path, tag: str) -> None:
    env = {"GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t"}
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=path, check=True)
    (path / "README.md").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=path, env={**env}, check=True)
    subprocess.run(["git", "tag", tag], cwd=path, check=True)


def _ctx(tmp_path: Path) -> CheckContext:
    return CheckContext(repo_root=tmp_path, changed_files=[])


def test_matching_rev_passes(tmp_path: Path) -> None:
    _init_git_with_tag(tmp_path, "v0.5.0")
    (tmp_path / "README.md").write_text(
        "- repo: https://example.com/x\n  rev: v0.5.0\n", encoding="utf-8"
    )
    cfg = PrecommitRevMatchesTagConfig(files=["README.md"])
    assert PrecommitRevMatchesTag(config=cfg).run(_ctx(tmp_path)) == []


def test_stale_rev_fires(tmp_path: Path) -> None:
    _init_git_with_tag(tmp_path, "v0.5.0")
    (tmp_path / "README.md").write_text(
        "- repo: https://example.com/x\n  rev: v0.1.0\n", encoding="utf-8"
    )
    cfg = PrecommitRevMatchesTagConfig(files=["README.md"])
    findings = PrecommitRevMatchesTag(config=cfg).run(_ctx(tmp_path))
    assert len(findings) == 1
    assert "v0.1.0" in findings[0].message
    assert "v0.5.0" in findings[0].message


def test_no_tags_returns_nothing(tmp_path: Path) -> None:
    env = {"GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t"}
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("rev: v0.1.0\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=tmp_path, env=env, check=True)
    cfg = PrecommitRevMatchesTagConfig(files=["README.md"])
    assert PrecommitRevMatchesTag(config=cfg).run(_ctx(tmp_path)) == []


def test_missing_file_skipped(tmp_path: Path) -> None:
    _init_git_with_tag(tmp_path, "v1.0")
    cfg = PrecommitRevMatchesTagConfig(files=["does-not-exist.yaml"])
    assert PrecommitRevMatchesTag(config=cfg).run(_ctx(tmp_path)) == []
