"""
AutoApply — FastAPI Backend
Main entry point. Wires together routes, middleware, WebSocket, and startup tasks.
"""

import logging
from contextlib import asynccontextmanager
import json as _json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from middleware import RequestLoggingMiddleware, ErrorHandlerMiddleware
from api.websocket_manager import ws_manager
from api.routes.users import router as users_router, user_store
from api.routes.jobs import router as jobs_router
from api.routes.voice import router as voice_router
from db.models import init_db
from services.s3_service import ensure_bucket_exists

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── App ───────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("AutoApply backend starting up...")
    try:
        await init_db()
        logger.info("Database tables verified/created")
    except Exception as e:
        logger.warning(f"DB init skipped (in-memory mode): {e}")
    try:
        ensure_bucket_exists()
    except Exception as e:
        logger.warning(f"S3 bucket check skipped: {e}")
    logger.info(
        f"Nova Act configured: {bool(settings.nova_act_api_key)} | "
        f"Bedrock configured: {bool(settings.aws_access_key_id)}"
    )
    logger.info("AutoApply ready ✓")
    yield
    # Shutdown (nothing needed for now)


app = FastAPI(
    title="AutoApply API",
    description="AI-powered job application agent powered by Amazon Nova Act and Nova 2 Lite",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware (order matters — outermost first) ───────────────────────────────
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(users_router)
app.include_router(jobs_router)
app.include_router(voice_router)




# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["system"])
async def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "nova_act_configured": bool(settings.nova_act_api_key),
        "bedrock_configured": bool(settings.aws_access_key_id),
        "s3_configured": bool(settings.s3_bucket_name and settings.aws_access_key_id),
    }


# ── WebSocket ─────────────────────────────────────────────────────────────────
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    Real-time agent event stream per user.
    Frontend connects here to receive live Nova Act progress updates.
    """
    await ws_manager.connect(websocket, user_id)
    try:
        await websocket.send_text('{"type":"connected","message":"Connected to AutoApply agent"}')
        while True:
            data = await websocket.receive_text()
            try:
                msg = _json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_text('{"type":"pong"}')
                elif msg.get("type") == "approve_application":
                    # Future: handle user approving a pending application
                    logger.info(f"User {user_id} approved application: {msg.get('job_id')}")
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id)
        logger.info(f"WebSocket disconnected: {user_id}")


# ── Dev runner ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.app_env == "development",
        log_level="info",
    )
