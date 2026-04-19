"""pr-sop CLI."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer

from pr_sop import __version__
from pr_sop.config import PrSopConfig
from pr_sop.engine import run_scan
from pr_sop.reporters import report

app = typer.Typer(
    name="pr-sop",
    help="Opinionated PR governance checks. Config-driven, no LLM.",
    no_args_is_help=True,
    add_completion=False,
)


@app.command()
def check(
    repo: Annotated[
        Path, typer.Option("--repo", help="Path to the git repo to scan.")
    ] = Path("."),
    config: Annotated[
        Path | None,
        typer.Option("--config", help="Path to .prsop.yml. Defaults to <repo>/.prsop.yml."),
    ] = None,
    base: Annotated[
        str | None,
        typer.Option(
            "--base",
            help="Base ref to diff against (e.g. origin/main). Omit to scan whole tree.",
        ),
    ] = None,
) -> None:
    """Run configured checks and report findings."""
    repo = repo.resolve()
    cfg_path = config or (repo / ".prsop.yml")
    cfg = PrSopConfig.load(cfg_path)

    result = run_scan(repo, cfg, base)
    report(result)
    sys.exit(result.exit_code)


@app.command()
def version() -> None:
    """Print pr-sop version."""
    typer.echo(__version__)


if __name__ == "__main__":
    app()
