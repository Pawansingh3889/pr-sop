"""Tests for precommit-rev-matches-tag check."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from pr_sop.checks.base import CheckContext
from pr_sop.checks.precommit_rev_matches import PrecommitRevMatchesTag
from pr_sop.config import PrecommitRevMatchesTagConfig


GIT_ENV = {
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@t",
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@t",
}


def _init_git(path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=path, check=True)
    (path / "README.md").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=path, env=GIT_ENV, check=True)


def _init_git_with_tag(path: Path, tag: str, origin: str | None = None) -> None:
    _init_git(path)
    subprocess.run(["git", "tag", tag], cwd=path, check=True)
    if origin:
        subprocess.run(["git", "remote", "add", "origin", origin], cwd=path, check=True)


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
    _init_git(tmp_path)
    (tmp_path / "README.md").write_text("rev: v0.1.0\n", encoding="utf-8")
    cfg = PrecommitRevMatchesTagConfig(files=["README.md"])
    assert PrecommitRevMatchesTag(config=cfg).run(_ctx(tmp_path)) == []


def test_missing_file_skipped(tmp_path: Path) -> None:
    _init_git_with_tag(tmp_path, "v1.0")
    cfg = PrecommitRevMatchesTagConfig(files=["does-not-exist.yaml"])
    assert PrecommitRevMatchesTag(config=cfg).run(_ctx(tmp_path)) == []


# ---------------------------------------------------------------------------
# Repo-URL filtering: the fix for pr-sop v0.1.0's false positives on
# third-party `rev:` pins inside .pre-commit-config.yaml.
# ---------------------------------------------------------------------------


def test_third_party_rev_not_flagged_when_origin_set(tmp_path: Path) -> None:
    """Stale `rev:` under a third-party `repo:` must be silent."""
    _init_git_with_tag(
        tmp_path,
        "v0.5.0",
        origin="https://github.com/acme/my-tool.git",
    )
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n"
        "  - repo: https://github.com/pre-commit/pre-commit-hooks\n"
        "    rev: v4.6.0\n"
        "  - repo: https://github.com/astral-sh/ruff-pre-commit\n"
        "    rev: v0.11.0\n",
        encoding="utf-8",
    )
    cfg = PrecommitRevMatchesTagConfig(files=[".pre-commit-config.yaml"])
    assert PrecommitRevMatchesTag(config=cfg).run(_ctx(tmp_path)) == []


def test_self_repo_stale_rev_still_flagged(tmp_path: Path) -> None:
    """Stale `rev:` under a self `repo:` must still fire."""
    _init_git_with_tag(
        tmp_path,
        "v0.5.0",
        origin="https://github.com/acme/my-tool.git",
    )
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n"
        "  - repo: https://github.com/acme/my-tool\n"
        "    rev: v0.4.0\n",
        encoding="utf-8",
    )
    cfg = PrecommitRevMatchesTagConfig(files=[".pre-commit-config.yaml"])
    findings = PrecommitRevMatchesTag(config=cfg).run(_ctx(tmp_path))
    assert len(findings) == 1
    assert findings[0].line == 3
    assert "v0.4.0" in findings[0].message


def test_mixed_repos_only_self_flagged(tmp_path: Path) -> None:
    """Third-party and self blocks in one file: only the self one fires."""
    _init_git_with_tag(
        tmp_path,
        "v0.5.0",
        origin="git@github.com:Acme/My-Tool.git",
    )
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n"
        "  - repo: https://github.com/pre-commit/pre-commit-hooks\n"
        "    rev: v4.6.0\n"
        "  - repo: https://github.com/acme/my-tool\n"
        "    rev: v0.4.0\n"
        "  - repo: https://github.com/astral-sh/ruff-pre-commit\n"
        "    rev: v0.11.0\n",
        encoding="utf-8",
    )
    cfg = PrecommitRevMatchesTagConfig(files=[".pre-commit-config.yaml"])
    findings = PrecommitRevMatchesTag(config=cfg).run(_ctx(tmp_path))
    assert len(findings) == 1
    assert "v0.4.0" in findings[0].message
    assert findings[0].line == 5


def test_repo_url_pattern_overrides_auto(tmp_path: Path) -> None:
    """Explicit `repo_url_pattern` wins over origin auto-detection."""
    _init_git_with_tag(
        tmp_path,
        "v0.5.0",
        origin="https://github.com/acme/my-tool.git",
    )
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n"
        "  - repo: https://github.com/acme/my-tool\n"
        "    rev: v0.4.0\n"
        "  - repo: https://github.com/other-org/other-tool\n"
        "    rev: v0.1.0\n",
        encoding="utf-8",
    )
    cfg = PrecommitRevMatchesTagConfig(
        files=[".pre-commit-config.yaml"],
        repo_url_pattern=r"other-org/other-tool",
    )
    findings = PrecommitRevMatchesTag(config=cfg).run(_ctx(tmp_path))
    assert len(findings) == 1
    assert "v0.1.0" in findings[0].message


def test_origin_ssh_and_config_https_match(tmp_path: Path) -> None:
    """SSH origin and HTTPS `repo:` for the same repo canonicalise the same."""
    _init_git_with_tag(
        tmp_path,
        "v0.5.0",
        origin="git@github.com:Owner/Name.git",
    )
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n"
        "  - repo: https://github.com/owner/name\n"
        "    rev: v0.4.0\n",
        encoding="utf-8",
    )
    cfg = PrecommitRevMatchesTagConfig(files=[".pre-commit-config.yaml"])
    findings = PrecommitRevMatchesTag(config=cfg).run(_ctx(tmp_path))
    assert len(findings) == 1


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("https://github.com/Owner/Name.git", "owner/name"),
        ("https://github.com/Owner/Name", "owner/name"),
        ("https://github.com/Owner/Name/", "owner/name"),
        ("git@github.com:Owner/Name.git", "owner/name"),
        ("git@github.com:owner/name", "owner/name"),
        ("ssh://git@github.com/Owner/Name", "owner/name"),
        ("owner/name", "owner/name"),
    ],
)
def test_normalise_repo_url(raw: str, expected: str) -> None:
    assert PrecommitRevMatchesTag._normalise_repo_url(raw) == expected
