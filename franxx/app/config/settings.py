import os
from pathlib import Path


def get_env_file() -> str:
    """
    Determine which .env file to load based on APP_ENVIRONMENT variable.

    Priority (two-stage loading):
    1. Check environment variable APP_ENVIRONMENT first (highest priority)
    2. If not set, peek into .env file to read APP_ENVIRONMENT from there
    3. Load .env.{APP_ENVIRONMENT} if it exists
    4. Fallback to .env if environment-specific file doesn't exist

    Usage:
        # Method 1: Set via environment variable (highest priority)
        APP_ENVIRONMENT=development uv run fastapi dev app/main.py  # loads .env.dev

        # Method 2: Set in .env file (easier for development)
        # In .env file: APP_ENVIRONMENT=development
        uv run fastapi dev app/main.py  # reads .env, sees APP_ENVIRONMENT=development, loads .env.dev

        # Method 3: No APP_ENVIRONMENT set
        uv run fastapi dev app/main.py  # loads .env (default)
    """
    # Stage 1: Check environment variable (highest priority)
    env = os.getenv("APP_ENVIRONMENT", "").lower()
    print(env)

    # Stage 2: If not in env var, peek into .env to check if APP_ENVIRONMENT is defined there
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
            pass  # If we can't read .env, just use default

    # Stage 3: Try to load environment-specific file
    if env:
        env_file = f".env.{env}"
        if Path(env_file).exists():
            return env_file

    # Stage 4: Fallback to .env
    return ".env"