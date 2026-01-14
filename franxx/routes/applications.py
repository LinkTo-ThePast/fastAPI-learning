from fastapi import APIRouter

## instantiate api router
router = APIRouter()

@router.post("/{vg_id}/user/{user_id}/documents/presign")
async def get_vg_document_presigned_url(
    vg_id: str,
    user_id: str,
):
    try:
        