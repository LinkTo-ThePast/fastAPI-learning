from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
	return {"message": "Clair Obscure"}

@app.get("/get-videogame/{vg_id}")
async def getVideogame(vg_id: str):
    vg = {"name": "Final Fantasy VII: Rebirth",
          "relesead_year:": 2024}
    return {"success": True, "data": vg, "vg_id": vg_id}
    