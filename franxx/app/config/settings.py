import os
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


def get_env_file() -> str:
    
    # --> check ENV first
    env = os.getenv("APP_ENVIRONMENT", "").lower()

    # IF NOT ENV defined, then review .env files
    if not env and Path(".env").exists():
        try:
            with open(".env", "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("APP_ENVIRONMENT="):
                        # Extract value after =, remove quotes if present
                        env = (
                            line.split("=", 1)[1].strip().strip('"').strip("'").lower()
                        )
                        break
        except Exception:
            pass  

    if env:
        env_file = f".env.{env}"
        if Path(env_file).exists():
            return env_file

    # Stage 4: Fallback to .env
    return ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
		env_file=get_env_file(),
		env_file_encoding="utf-8",
		env_prefix="APP_",
		case_sensitive=False,
		extra="ignore",
	)
    
    environment: str = Field(default="local", description="Environment: local, stage, dev, prod")
    
    videogame_id: str | None = Field(default=None ,description="Unique identifier for videogame.")
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, environment_value: str) -> str:
        allowed_env_values = [
            "local",
            "dev",
            "development",
            "stage",
            "production",
            "prod"
        ]
        
        if environment_value not in allowed_env_values:
            raise ValueError(f"Environment value must be one of the following: {allowed_env_values}")
        
        if environment_value == "production":
            return "prod"
        if environment_value == "development":
            return "dev"
        return environment_value  