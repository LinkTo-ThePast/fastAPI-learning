from app.schemas.health import HealthStatus
from fastapi import APIRouter, status

router = APIRouter()

@router.get("/", response_model=HealthStatus, status_code=status.HTTP_200_OK)
async def liveness() -> HealthStatus:
    """
    Verify process is running OK
	Returns: health status check
    """
    return HealthStatus(status="OK!")