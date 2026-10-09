import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.core.retention import cleanup_once
from app.db.session import SessionLocal
from app.modules.auth.router import router as auth_router
from app.modules.auth.service import bootstrap_admin
from app.modules.devices.router import router as device_router
from app.modules.health.router import router as health_router
from app.modules.metrics.router import router as metrics_router

logger = logging.getLogger(__name__)


def initialize_admin():
    with SessionLocal() as db:
        bootstrap_admin(db)


async def cleanup_loop(stop: asyncio.Event):
    while not stop.is_set():
        await asyncio.to_thread(cleanup_once)
        try:
            await asyncio.wait_for(stop.wait(), timeout=settings.cleanup_interval_seconds)
        except TimeoutError:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.admin_password:
        await asyncio.to_thread(initialize_admin)
    stop = asyncio.Event()
    task = asyncio.create_task(cleanup_loop(stop)) if settings.cleanup_enabled else None
    yield
    stop.set()
    if task:
        await task


class BodyLimitMiddleware:

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] not in {"POST", "PUT", "PATCH"}:
            return await self.app(scope, receive, send)
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            body.extend(message.get("body", b""))
            if len(body) > settings.max_request_bytes:
                return await JSONResponse(
                    status_code=413, content={"detail": "Request body too large"}
                )(scope, receive, send)
            if not message.get("more_body", False):
                break
        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, replay, send)


app = FastAPI(title="Мониторинговый сервис", version="0.2.0", lifespan=lifespan)
app.add_middleware(BodyLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Agent-Token"],
    expose_headers=["X-Total-Count"],
)


@app.exception_handler(SQLAlchemyError)
async def database_error(request: Request, error: SQLAlchemyError):
    logger.warning("Database operation failed (%s)", type(error).__name__)
    return JSONResponse(status_code=503, content={"detail": "Database temporarily unavailable"})


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, error: RequestValidationError):
    safe = [{"loc": item["loc"], "msg": item["msg"], "type": item["type"]} for item in error.errors()]
    return JSONResponse(status_code=422, content={"detail": safe})


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(device_router)
app.include_router(metrics_router)
