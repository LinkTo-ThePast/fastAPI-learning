## modules of our app
from app.routes.videogames import router as videogames_router

from fastapi import FastAPI


app = FastAPI()
app.include_router(videogames_router)

@app.get("/health")
def health_check():
    return { "status": "ok" }