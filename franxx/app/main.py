from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging


from app.routes.videogames import router as videogames_router
from app.config.settings import get_settings

## schedule
scheduler: AsyncIOScheduler | None = None

## initialize settings
settings = get_settings() 
## initialize logging
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(videogames_router)


@app.get("/health")
def health_check():
    return { "status": "ok" }