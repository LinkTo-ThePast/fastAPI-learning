from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

from app.routes import (
    health,
    videogames
)
from app.config.settings import get_settings

## schedule
scheduler: AsyncIOScheduler | None = None

## initialize settings
settings = get_settings() 
## initialize logging
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(videogames.router, prefix="/videogames", tags=["videogames", "videogames_information"])


@app.get("/health")
def health_check():
    return { "status": "ok" }