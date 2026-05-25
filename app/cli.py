from __future__ import annotations

import json

import typer
from alembic.config import main as alembic_main
from rich.console import Console
from rich.table import Table
from sqlalchemy import select

from .config import settings
from .db import get_session
from .enums import RunStatus
from .models import Config, Itinerary, Run
from .orchestrator.runner import execute_run
from .seed import seed_all
from .sources.quota import QuotaTracker

cli = typer.Typer(help="Trip Planner — MLFO Phase 1 CLI")
db_app = typer.Typer(help="Database migrations (Alembic shim).")
cli.add_typer(db_app, name="db")
console = Console()


@db_app.command("upgrade")
def db_upgrade(revision: str = "head"):
    """Upgrade the database to a given revision (default: head)."""
    alembic_main(["upgrade", revision])


@db_app.command("revision")
def db_revision(
    message: str = typer.Option(..., "-m", "--message", help="Revision message"),
    autogenerate: bool = typer.Option(False, "--autogenerate", help="Autogenerate from model diff"),
):
    """Create a new Alembic revision."""
    argv = ["revision", "-m", message]
    if autogenerate:
        argv.append("--autogenerate")
    alembic_main(argv)


@cli.command()
def seed():
    """Seed the engagement configs (Structures A and B)."""
    ids = seed_all()
    console.print(
        f"[green]Seeded[/green]: A=config #{ids['A']}, B=config #{ids['B']}, "
        f"Venice=config #{ids.get('Venice', '?')}"
    )


@cli.command()
def configs():
    """List configs."""
    table = Table("ID", "Name", "Budget", "Pax", "Structures")
    with get_session() as s:
        for c in s.scalars(select(Config).order_by(Config.id)).all():
            table.add_row(str(c.id), c.name, f"${c.budget_party_total:,}",
                          json.dumps(c.passengers), ",".join(c.structures))
    console.print(table)


@cli.command()
def quota():
    """Show SerpAPI quota status."""
    from .orchestrator.runner import _sum_used_serpapi_calls
    with get_session() as s:
        used = _sum_used_serpapi_calls(s)
    q = QuotaTracker(ceiling=settings.serpapi_monthly_ceiling, used_before_run=used)
    console.print(f"SerpAPI ceiling: [bold]{q.ceiling}[/bold]")
    console.print(f"Used (completed runs this DB): [bold]{used}[/bold]")
    console.print(f"Remaining: [bold]{q.remaining}[/bold]")
    if not settings.serpapi_key:
        console.print("[yellow]No SERPAPI_KEY set — validation pass will be skipped.[/yellow]")


@cli.command()
def run(config_id: int):
    """Execute a run synchronously and print the top results."""
    with get_session() as s:
        r = Run(config_id=config_id, config_snapshot={}, status=RunStatus.PENDING.value)
        s.add(r)
        s.commit()
        s.refresh(r)
        run_id = r.id

    console.print(f"[cyan]Starting run #{run_id} for config {config_id}…[/cyan]")
    try:
        execute_run(run_id, get_session)
    except Exception as e:
        console.print(f"[red]Run failed:[/red] {e}")
        raise typer.Exit(code=1)

    with get_session() as s:
        finished = s.get(Run, run_id)
        itineraries = s.scalars(
            select(Itinerary).where(Itinerary.run_id == run_id).order_by(Itinerary.rank).limit(10)
        ).all()

    console.print(f"[green]Run #{run_id} {finished.status}[/green] · "
                  f"scraper={finished.scraper_calls} · serpapi={finished.serpapi_calls} "
                  f"· remaining={finished.serpapi_quota_remaining}")

    table = Table("Rank", "Struct", "Status", "Gateway", "Party total", "Flags")
    for it in itineraries:
        table.add_row(
            str(it.rank), it.structure, it.verification_status, it.gateway or "—",
            f"${it.total_party_price:,}", ",".join(it.flags) or "—",
        )
    console.print(table)
    console.print(f"View in browser: [link]http://127.0.0.1:8000/runs/{run_id}[/link]")


@cli.command()
def serve(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Start the FastAPI server."""
    import uvicorn
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    cli()
