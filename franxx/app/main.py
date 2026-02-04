## modules of our app
from app.routes.videogames import router as videogames_router
from app.config.settings import get_env_file
from fastapi import FastAPI


app = FastAPI()
app.include_router(videogames_router)


current_env = get_env_file()
print(f"current env is: {current_env}")

@app.get("/health")
def health_check():
    return { "status": "ok" }