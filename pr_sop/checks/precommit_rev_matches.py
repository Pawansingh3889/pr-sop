"""precommit-rev-matches-tag: `rev:` pins referencing this repo must match latest git tag."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
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

        repo_matches: Callable[[str], bool] = self._build_repo_matcher(ctx.repo_root)

        findings: list[Finding] = []
        repo_line = re.compile(r"repo:\s*['\"]?([^'\"\s]+)['\"]?")
        rev_line = re.compile(r"rev:\s*['\"]?([^'\"\s]+)['\"]?")

        for file_rel in self.config.files:
            path = ctx.repo_root / file_rel
            if not path.exists():
                continue

            current_matches = True
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                m_repo = repo_line.search(line)
                if m_repo:
                    current_matches = repo_matches(m_repo.group(1))
                    continue

                m_rev = rev_line.search(line)
                if not m_rev or not current_matches:
                    continue
                rev = m_rev.group(1)
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

    def _build_repo_matcher(self, repo_root) -> Callable[[str], bool]:
        """Return url -> bool deciding whether a `repo:` entry references this repo.

        Priority: explicit `repo_url_pattern` regex, then git origin URL auto-detect,
        then a permissive default that keeps the legacy behaviour for callers with
        no remote and no pattern configured.
        """
        assert self.config is not None
        pattern = self.config.repo_url_pattern.strip()
        if pattern:
            regex = re.compile(pattern)
            return lambda url: regex.search(url) is not None

        origin = self._origin_url(repo_root)
        if origin:
            origin_key = self._normalise_repo_url(origin)
            return lambda url: self._normalise_repo_url(url) == origin_key

        return lambda _url: True

    @staticmethod
    def _latest_tag(repo_root) -> str | None:
        """Return the highest semver-style tag in the repo.

        Uses `git tag --sort=-v:refname` (natural version sort, descending)
        rather than `git describe --tags --abbrev=0`. The describe approach
        requires the tag to be reachable from HEAD, which breaks in GitHub
        Actions PR runs: the ephemeral merge commit GitHub creates for
        `pull_request` events often does not have the latest release tag in
        its ancestry, so describe silently fails and the check returned
        zero findings even when drift was present (pr-sop #issue-forthcoming).

        The version-sorted listing is resilient to that: it reports the
        highest tag regardless of whether HEAD can reach it, which is also
        the right semantic for "does your rev pin match the most recent
        release?".
        """
        try:
            result = subprocess.run(
                ["git", "tag", "--sort=-v:refname"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            return None
        if result.returncode != 0:
            return None
        first_line = result.stdout.strip().splitlines()
        return first_line[0] if first_line else None

    @staticmethod
    def _origin_url(repo_root) -> str | None:
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
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

    @staticmethod
    def _normalise_repo_url(url: str) -> str:
        """Reduce any of the common remote URL shapes to a lowercased `owner/name`.

        Handles forms like `https://github.com/Owner/Name.git`,
        `git@github.com:Owner/Name.git`, `ssh://git@github.com/Owner/Name`,
        and bare `Owner/Name`.
        """
        s = url.strip().lower().rstrip("/")
        if s.endswith(".git"):
            s = s[:-4]

        if s.startswith("git@") and ":" in s:
            _, _, path = s.partition(":")
            return path

        if "://" in s:
            _, _, after_scheme = s.partition("://")
            _, _, path = after_scheme.partition("/")
            return path

        return s
