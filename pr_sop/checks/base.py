"""Check interface and Finding dataclass."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class Finding:
    check_id: str
    severity: str  # "error" | "warning"
    message: str
    file: str | None = None
    line: int | None = None
    suggestion: str | None = None


@dataclass(frozen=True)
class CheckContext:
    """Everything a check needs from the repo."""

    repo_root: Path
    changed_files: list[str]  # paths relative to repo_root


class Check(Protocol):
    check_id: str

    def run(self, ctx: CheckContext) -> list[Finding]: ...
