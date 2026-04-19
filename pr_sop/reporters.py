"""Output reporters: terminal (Rich) and GitHub Actions workflow commands."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from rich.console import Console

from pr_sop.engine import ScanResult


def report_terminal(result: ScanResult, console: Console | None = None) -> None:
    console = console or Console()

    if not result.findings:
        console.print(f"[green]OK[/green]  {len(result.checks_run)} check(s) passed.")
        return

    for f in result.findings:
        sev = f.severity.upper()
        colour = "red" if f.severity == "error" else "yellow"
        loc_parts = []
        if f.file:
            loc_parts.append(f.file)
        if f.line:
            loc_parts.append(str(f.line))
        loc = ":".join(loc_parts) if loc_parts else "-"
        console.print(
            f"[{colour}]{sev}[/{colour}]  [cyan]{f.check_id}[/cyan]  "
            f"[dim]{loc}[/dim]  {f.message}"
        )
        if f.suggestion:
            console.print(f"       [dim]-> {f.suggestion}[/dim]")

    console.print()
    console.print(
        f"[bold]{result.error_count}[/bold] error(s), "
        f"[bold]{result.warning_count}[/bold] warning(s) "
        f"across {len(result.checks_run)} check(s)."
    )


def report_github(result: ScanResult) -> None:
    """Emit workflow commands + write to $GITHUB_STEP_SUMMARY."""
    for f in result.findings:
        level = "error" if f.severity == "error" else "warning"
        parts = [f"title={f.check_id}"]
        if f.file:
            parts.append(f"file={f.file}")
        if f.line:
            parts.append(f"line={f.line}")
        cmd = f"::{level} {','.join(parts)}::{f.message}"
        print(cmd)

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        _write_step_summary(Path(summary_path), result)


def _write_step_summary(path: Path, result: ScanResult) -> None:
    lines = ["# pr-sop\n"]
    if not result.findings:
        lines.append(f"OK. {len(result.checks_run)} check(s) passed.\n")
    else:
        lines.append(
            f"**{result.error_count}** error(s), **{result.warning_count}** warning(s) "
            f"across {len(result.checks_run)} check(s).\n"
        )
        lines.append("| Severity | Check | Location | Message |")
        lines.append("| --- | --- | --- | --- |")
        for f in result.findings:
            loc = f.file or ""
            if f.line:
                loc = f"{loc}:{f.line}" if loc else str(f.line)
            msg = f.message.replace("|", "\\|")
            lines.append(f"| {f.severity} | `{f.check_id}` | `{loc}` | {msg} |")
    with path.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def in_github_actions() -> bool:
    return os.environ.get("GITHUB_ACTIONS") == "true"


def report(result: ScanResult) -> None:
    if in_github_actions():
        report_github(result)
    report_terminal(result, Console(file=sys.stdout))
