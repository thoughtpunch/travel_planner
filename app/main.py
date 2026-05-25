from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles  # noqa: F401
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect, select
from starlette.requests import Request

from .api import configs as configs_api
from .api import copilot as copilot_api
from .api import quota as quota_api
from .api import runs as runs_api
from .api import trips as trips_api
from .db import engine, get_session

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def _assert_migrations_applied() -> None:
    inspector = inspect(engine)
    if "alembic_version" not in inspector.get_table_names():
        raise RuntimeError(
            "Database has no `alembic_version` table. "
            "Run `mise run migrate` (or `alembic upgrade head`) before starting the server."
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    _assert_migrations_applied()
    yield


app = FastAPI(title="Trip Planner — MLFO Phase 1", lifespan=lifespan)

app.include_router(configs_api.router)
app.include_router(runs_api.router)
app.include_router(quota_api.router)
app.include_router(trips_api.router)
app.include_router(copilot_api.router)

# SPA static + catch-all. The SPA build lands at app/static/web-dist/ via
# `mise run web:build`; if absent, Jinja UI remains the surface.
STATIC_DIR = Path(__file__).parent / "static"
SPA_DIR = STATIC_DIR / "web-dist"
if SPA_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(SPA_DIR / "assets")), name="spa-assets")

TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    from .models import Config, Run

    with get_session() as session:
        configs = session.scalars(select(Config).order_by(Config.id)).all()
        runs = session.scalars(select(Run).order_by(Run.id.desc()).limit(20)).all()
    return templates.TemplateResponse(request, "home.html", {
        "configs": configs,
        "runs": runs,
    })


@app.get("/runs/{run_id}", response_class=HTMLResponse)
def view_run(request: Request, run_id: int):
    from .api.runs import _build_results_payload

    payload = _build_results_payload(run_id)
    return templates.TemplateResponse(request, "run.html", {
        "results": payload,
    })


# SPA catch-all: every non-`/api/*` path that does not match a Jinja route
# falls through to the SPA's index.html so client-side routing works on
# direct URL entry (e.g. an emailed /trips/42/runs/7 link).
@app.get("/trips/{full_path:path}", response_class=HTMLResponse)
@app.get("/settings/{full_path:path}", response_class=HTMLResponse)
@app.get("/wizard/{full_path:path}", response_class=HTMLResponse)
def spa_catchall(request: Request, full_path: str):
    index = SPA_DIR / "index.html"
    if index.exists():
        return HTMLResponse(content=index.read_text(), status_code=200)
    return HTMLResponse(
        content=(
            "<!doctype html><meta charset=utf-8>"
            "<h1>SPA not built</h1>"
            "<p>Run <code>mise run web:build</code> to build the Vue 3 + PrimeVue SPA.</p>"
            "<p><a href='/'>Go to Phase-1 Jinja UI</a></p>"
        ),
        status_code=503,
    )
