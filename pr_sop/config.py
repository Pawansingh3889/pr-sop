"""Config schema for .prsop.yml."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field


Severity = Literal["error", "warning", "off"]


class ChangelogRequiredConfig(BaseModel):
    severity: Severity = "error"
    paths: list[str] = Field(
        default_factory=lambda: ["**/*.py"],
        description="Glob patterns. If any changed path matches, a CHANGELOG entry is required.",
    )
    changelog_file: str = "CHANGELOG.md"
    unreleased_heading: str = "## [Unreleased]"


class VersionConsistencyConfig(BaseModel):
    severity: Severity = "error"
    sources: list[dict[str, str]] = Field(
        default_factory=list,
        description=(
            "List of {file, pattern} entries. `pattern` is a regex with one capture "
            "group that extracts the version string."
        ),
    )


class PrecommitRevMatchesTagConfig(BaseModel):
    severity: Severity = "warning"
    files: list[str] = Field(
        default_factory=lambda: ["README.md", ".pre-commit-hooks.yaml"],
        description="Files to scan for `rev:` references to this repo.",
    )
    repo_url_pattern: str = Field(
        default=r"",
        description="Regex matching the repo URL. If empty, auto-detected from git remote.",
    )


class ChecksConfig(BaseModel):
    changelog_required: ChangelogRequiredConfig | None = None
    version_consistency: VersionConsistencyConfig | None = None
    precommit_rev_matches_tag: PrecommitRevMatchesTagConfig | None = None


class PrSopConfig(BaseModel):
    checks: ChecksConfig = Field(default_factory=ChecksConfig)

    @classmethod
    def load(cls, path: Path) -> PrSopConfig:
        if not path.exists():
            return cls()
        with path.open() as f:
            raw: dict[str, Any] = yaml.safe_load(f) or {}
        return cls.model_validate(raw)
