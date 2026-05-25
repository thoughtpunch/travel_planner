from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from .api import configs as configs_api
from .api import quota as quota_api
from .api import runs as runs_api
from .db import get_session, init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Trip Planner — MLFO Phase 1", lifespan=lifespan)

app.include_router(configs_api.router)
app.include_router(runs_api.router)
app.include_router(quota_api.router)

TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    from sqlmodel import select

    from .models import Config, Run

    with get_session() as session:
        configs = session.exec(select(Config).order_by(Config.id)).all()
        runs = session.exec(select(Run).order_by(Run.id.desc()).limit(20)).all()
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
