import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import wait_for_db
from app.routes.events import router as events_router
from app.routes.health import router as health_router
from app.routes.pixel import router as pixel_router
from app.routes.track import router as track_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

app = FastAPI(title="pixel-tracking-lab", version="1.0.0")

origins = [origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(track_router)
app.include_router(pixel_router)
app.include_router(events_router)


@app.on_event("startup")
def startup_event() -> None:
    """Retry DB connection on startup so Compose boot order is less fragile."""
    wait_for_db()
