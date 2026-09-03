from __future__ import annotations

import base64
import hmac
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import inspect
from starlette.requests import Request

from .api import wiki as wiki_api
from .config import settings
from .db import engine
from .wiki_seed import seed_wiki

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
    seed_wiki()
    yield


app = FastAPI(title="Italy 2026 Trip Wiki", lifespan=lifespan)


@app.middleware("http")
async def family_login(request: Request, call_next):
    """Protect trip details when APP_PASSWORD is configured (as it is on Fly)."""
    if not settings.app_password or request.url.path == "/healthz":
        return await call_next(request)
    authorization = request.headers.get("authorization", "")
    authenticated = False
    if authorization.startswith("Basic "):
        try:
            decoded = base64.b64decode(authorization[6:], validate=True).decode("utf-8")
            username, password = decoded.split(":", 1)
            authenticated = hmac.compare_digest(username, settings.app_username) and hmac.compare_digest(
                password, settings.app_password
            )
        except (ValueError, UnicodeDecodeError):
            authenticated = False
    if not authenticated:
        return JSONResponse(
            {"detail": "Family login required"}, status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="Italy 2026", charset="UTF-8"'},
        )
    response = await call_next(request)
    if request.url.path.startswith("/api/") or response.headers.get("content-type", "").startswith("text/html"):
        response.headers["Cache-Control"] = "no-store"
    return response

app.include_router(wiki_api.router)

if settings.enable_legacy_fare_api:
    from .api import configs as configs_api
    from .api import copilot as copilot_api
    from .api import quota as quota_api
    from .api import runs as runs_api
    from .api import trips as trips_api

    app.include_router(configs_api.router)
    app.include_router(runs_api.router)
    app.include_router(quota_api.router)
    app.include_router(trips_api.router)
    app.include_router(copilot_api.router)

# SPA static + catch-all. The wiki build lands at app/static/wiki-dist/.
STATIC_DIR = Path(__file__).parent / "static"
SPA_DIR = STATIC_DIR / "wiki-dist"
if (SPA_DIR / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=str(SPA_DIR / "assets")), name="spa-assets")

TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _wiki_index() -> HTMLResponse:
    index = SPA_DIR / "index.html"
    if index.exists():
        return HTMLResponse(content=index.read_text(encoding="utf-8"), status_code=200)
    return HTMLResponse(
        content=(
            "<!doctype html><meta charset=utf-8><h1>Italy wiki not built</h1>"
            "<p>Run <code>mise run wiki:build</code>.</p>"
        ),
        status_code=503,
    )


@app.get("/", response_class=HTMLResponse)
def home():
    return _wiki_index()


@app.get("/healthz")
def healthz():
    return {"status": "ok", "storage": "sqlite"}


@app.get("/runs/{run_id}", response_class=HTMLResponse)
def view_run(request: Request, run_id: int):
    from .api.runs import _build_results_payload

    payload = _build_results_payload(run_id)
    return templates.TemplateResponse(request, "run.html", {
        "results": payload,
    })


@app.get("/{full_path:path}", response_class=HTMLResponse)
def spa_catchall(full_path: str):
    return _wiki_index()
