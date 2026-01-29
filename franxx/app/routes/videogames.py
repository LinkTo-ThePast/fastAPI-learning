from pydantic import BaseModel
from typing import List
from fastapi import APIRouter

class VideoGame(BaseModel):
    id: int
    title: str

videogames_list: List[VideoGame] = [
    VideoGame(id=1, title="Ninja Gaiden 2 Black"),
    VideoGame(id=2, title="The Legend of Zelda: Ocarina of Time"),
    VideoGame(id=3, title="Luigi's Mansion") 
]

router = APIRouter(prefix="/api/v1/videogames", tags=["videogames"]) 

@router.get("/list-videogames")
async def get_list_videogames():
    return videogames_list


@router.get("/list-videogames/{id}")
async def get_videogame_by_id(id: int):
    for entry in videogames_list:
        if entry.id == id:
            return entry
    return {"success": False, "message": "Please, provide a valid ID!"}