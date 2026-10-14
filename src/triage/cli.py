"""CLI: thin adapter over classify + slice + render."""
from __future__ import annotations

import json
import sys

import typer

from .classify import triage
from .render import write_markdown
from .slice import to_tickets
from .sources import from_gh_json, from_paste

app = typer.Typer(help="Raw issues to agent-ready tickets")


def _read_input(path: str | None) -> list[dict]:
    raw = open(path).read() if path else sys.stdin.read()
    raw = raw.strip()
    if not raw:
        typer.echo("empty input", err=True)
        raise typer.Exit(2)
    if raw.startswith("["):
        return from_gh_json(raw)
    pasted = from_paste(raw)
    if pasted:
        return pasted
    # single bare line = one issue with no body
    return [{"id": "p1", "title": raw.splitlines()[0][:120], "body": ""}]


@app.command()
def triage_cmd(
    path: str | None = typer.Argument(None, help="File with gh JSON or pasted text (default: stdin)"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Classify each Raw issue into a triage role with reasons."""
    try:
        issues = _read_input(path)
    except ValueError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(2)
    verdicts = [{"id": i["id"], "title": i["title"], **triage(i)} for i in issues]
    if as_json:
        typer.echo(json.dumps(verdicts, indent=2))
        return
    for v in verdicts:
        typer.echo(f"[{v['role']}] #{v['id']} {v['title']} — {'; '.join(v['reasons'])}")


@app.command(name="to-tickets")
def to_tickets_cmd(
    path: str | None = typer.Argument(None, help="File with gh JSON or pasted text (default: stdin)"),
    feature: str = typer.Option("inbox", "--feature"),
    out_dir: str | None = typer.Option(None, "--out-dir", help="Write files here (default: print)"),
) -> None:
    """Emit numbered ticket files for the ready-for-agent set."""
    try:
        issues = _read_input(path)
    except ValueError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(2)
    ready, skipped = [], 0
    for i in issues:
        if triage(i)["role"] == "ready-for-agent":
            ready.append(i)
        else:
            skipped += 1
    tickets = to_tickets(ready)
    files = write_markdown(tickets, feature)
    if out_dir:
        import os
        for rel, text in files.items():
            dest = os.path.join(out_dir, os.path.relpath(rel, f".scratch/{feature}"))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w") as f:
                f.write(text)
        typer.echo(f"wrote {len(files)} tickets ({skipped} non-ready skipped)")
        return
    for rel, text in files.items():
        typer.echo(f"--- {rel} ---\n{text}")


if __name__ == "__main__":
    app()
