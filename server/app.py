from datetime import datetime
import os
import sys
import time
import traceback
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from starlette.types import Scope, Receive, Send
from sqlalchemy import event as sa_event

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from server.api.auditoria import router as auditoria_router
from server.api.auth import router as auth_router, get_current_user
from server.api.backup_api import router as backup_router
from server.api.config import router as config_router
from server.api.debug_api import router as debug_router
from server.api.files import router as files_router
from server.api.health import router as health_router
from server.api.logs_api import router as logs_router
from server.api.scheduler import router as scheduler_router

import src.config as cfg
from server.core.cleanup import cleanup_old_files
from server.core.database import User, engine, get_session, hash_api_key, init_db
from server.core.debug_events import add_event
from server.core.log_core import add_log, rotate_logs
from server.core.scheduler_core import init_scheduler, stop_scheduler

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# ── SQLAlchemy query logger ──
@sa_event.listens_for(engine, "before_execute")
def before_sql(conn, clause, multiparams, params):
    conn.info.setdefault("_debug_start", time.time())


@sa_event.listens_for(engine, "after_execute")
def after_sql(conn, clause, multiparams, params, result):
    duration = (time.time() - conn.info.get("_debug_start", time.time())) * 1000
    sql = str(clause)
    if len(sql) > 300:
        sql = sql[:300] + "..."
    add_event("db_query", {
        "sql": sql,
        "params": str(params) if params else None,
        "duration_ms": round(duration, 2),
    }, source="database")


# ── Global exception hook ──
_original_excepthook = sys.excepthook
def _debug_excepthook(exc_type, exc_value, exc_tb):
    tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    add_event("error", {"message": str(exc_value), "traceback": tb_text}, source="system")
    if _original_excepthook:
        _original_excepthook(exc_type, exc_value, exc_tb)
sys.excepthook = _debug_excepthook


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    _ensure_admin_user()
    rotate_logs()
    add_event("info", {"message": "Sistema ECOdata iniciado"}, "sistema")
    deleted = cleanup_old_files(cfg.OUTPUT_DIR)
    if deleted > 0:
        add_log("INFO", f"Limpeza de arquivos antigos: {deleted} removidos", "sistema")
    add_log("INFO", "Sistema ECOdata iniciado", "sistema")
    init_scheduler()
    add_log("INFO", "Agendador inicializado", "scheduler")
    yield
    add_log("INFO", "Sistema ECOdata encerrando...", "sistema")
    add_event("info", {"message": "Sistema ECOdata encerrando"}, "sistema")
    stop_scheduler()
    from src.db import close_pool

    close_pool()
    add_log("INFO", "Pool de conexoes fechado", "sistema")


def _ensure_api_key() -> str:
    import secrets
    api_key_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", ".api_key"
    )
    if os.path.exists(api_key_path):
        for line in open(api_key_path):
            if line.startswith("API Key:"):
                return line.split(":", 1)[1].strip()
    api_key = "ecodata_" + secrets.token_hex(32)
    os.makedirs(os.path.dirname(api_key_path), exist_ok=True)
    with open(api_key_path, "w") as f:
        f.write(f"API Key: {api_key}\n")
        f.write("Username: admin\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
    return api_key


def _ensure_admin_user():
    api_key = _ensure_api_key()
    session = get_session()
    try:
        existing = session.query(User).filter(User.username == "admin").first()
        if not existing:
            session.add(User(
                username="admin",
                api_key_hash=hash_api_key(api_key),
                role="admin",
                is_active=True,
            ))
            session.commit()
    finally:
        session.close()


app = FastAPI(
    title="ECOdata",
    description="Interface de gerenciamento ECOdata - Tradefy",
    version="1.0.0",
    lifespan=lifespan,
)

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:8580").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Debug middleware: captura toda request/response ──
@app.middleware("http")
async def debug_middleware(request: Request, call_next):
    start = time.time()
    path = request.url.path
    qs = str(request.url.query)
    method = request.method

    body_bytes = b""
    try:
        body_bytes = await request.body()
    except Exception:
        pass
    body_str = body_bytes.decode("utf-8", errors="replace") if body_bytes else None
    if body_str and len(body_str) > 500:
        body_str = body_str[:500] + "..."

    add_event("api_request", {
        "method": method,
        "path": path,
        "query": qs[:200] if qs else None,
        "body": body_str,
    }, source="http")

    try:
        response = await call_next(request)
    except Exception as exc:
        tb = traceback.format_exc()
        add_event("error", {"message": str(exc), "traceback": tb}, source="http")
        raise

    duration = (time.time() - start) * 1000
    resp_body = b""
    if hasattr(response, "body"):
        resp_body = response.body or b""
    body_out = resp_body.decode("utf-8", errors="replace") if resp_body else None
    if body_out and len(body_out) > 300:
        body_out = body_out[:300] + "..."

    add_event("api_response", {
        "method": method,
        "path": path,
        "status": response.status_code,
        "duration_ms": round(duration, 2),
        "body": body_out,
    }, source="http")

    return response


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(scheduler_router, dependencies=[Depends(get_current_user)])
app.include_router(auditoria_router, dependencies=[Depends(get_current_user)])
app.include_router(logs_router, dependencies=[Depends(get_current_user)])
app.include_router(debug_router, dependencies=[Depends(get_current_user)])
app.include_router(files_router, dependencies=[Depends(get_current_user)])
app.include_router(backup_router, dependencies=[Depends(get_current_user)])
app.include_router(config_router, dependencies=[Depends(get_current_user)])

class NoCacheStaticFiles(StaticFiles):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def send_no_cache(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                headers[b"Cache-Control"] = b"no-cache, no-store, must-revalidate"
                headers[b"Pragma"] = b"no-cache"
                headers[b"Expires"] = b"0"
                message["headers"] = [(k, v) for k, v in headers.items()]
            await send(message)
        await super().__call__(scope, receive, send_no_cache)


if os.path.exists(STATIC_DIR):
    app.mount("/", NoCacheStaticFiles(directory=STATIC_DIR, html=True), name="static")


def main():
    port = int(os.getenv("ECODATA_PORT", "8580"))
    host = os.getenv("ECODATA_HOST", "0.0.0.0")
    print(f"ECOdata iniciando em http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()