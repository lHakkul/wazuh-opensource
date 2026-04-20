import logging
from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import cluster, agents, manager, overview, history, alerts

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger(__name__)

_bg_task = None


async def _background_monitor():
    from app.routers.overview import get_overview
    while True:
        try:
            await get_overview()
        except Exception as e:
            logger.warning(f"Background monitor error: {e}")
        await asyncio.sleep(settings.ALERT_CHECK_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _bg_task
    _bg_task = asyncio.create_task(_background_monitor())
    logger.info("Background monitor started")
    yield
    if _bg_task:
        _bg_task.cancel()


app = FastAPI(
    title="Wazuh Pulse Monitor",
    description="API para monitorear el estado del ecosistema Wazuh",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(overview.router)
app.include_router(cluster.router)
app.include_router(agents.router)
app.include_router(manager.router)
app.include_router(history.router)
app.include_router(alerts.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "wazuh-pulse-monitor"}
