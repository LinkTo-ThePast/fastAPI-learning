from pydantic import BaseModel

class HealthStatus(BaseModel):
    """Basic check health status"""
    
    status: str


class ReadinessStatus(BaseModel):
    """Readiness check response with database status"""
    
    status: str
    database: str
    error: str | None = None