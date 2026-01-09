from enum import Enum
from fastapi import FastAPI

app = FastAPI()


class VideogameGenre(str, Enum):
    RPG = "rpg"
    ACTION = "action"
    SURVIVAL_HORROR = "survival-horror"
    
@app.get("/")
async def root():
	return {"message": "Clair Obscure"}

@app.get("/get-videogame/{vg_id}")
async def getVideogame(vg_id: str):
    vg = {"name": "Final Fantasy VII: Rebirth",
          "relesead_year:": 2024}
    return {"success": True, "data": vg, "vg_id": vg_id}

@app.get("/get-videogame-genre/{vg_genre}")
async def getVideogameGenre(vg_genre: VideogameGenre):
    if vg_genre == VideogameGenre.RPG:
        return {"success": True, "genre": VideogameGenre.RPG, "description": "Immersive world and history"}
    if vg_genre is VideogameGenre.SURVIVAL_HORROR:
        return {"success": True, "genre": VideogameGenre.SURVIVAL_HORROR.value, "description": "limited resources, dread"}
    return {"sucess": True, "genre": VideogameGenre.ACTION.value, "description": "fast combos and skills" }
        