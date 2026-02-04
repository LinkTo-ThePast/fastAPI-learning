import os
import ssl
from urllib.parse import urlparse
from typing import Optional, AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
  create_async_engine,
  AsyncEngine,
  AsyncSession,
  async_sessionmaker,
)

from app.config.settings import get_settings
import logging
"""
Configure postgreSQL with fastAPI

"""

logger = logging.getLogger(__name__)
settings = get_settings()

# Module-level singletons
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None

def get_engine() -> AsyncEngine:
	"""Return async engine, creating if needed"""
	global _engine
	
	if _engine is None:
		if not settings.database_url:
			raise RuntimeError(
				"APP_DATABASE_URL is empty"
			)
		
		connect_args = {}
		
		ca_path = settings.rds_ca_path
		if ca_path and os.path.exists(ca_path):
			ctx = ssl.create_default_context(cafile=ca_path)
			ctx.check_hostname = True
			ctx.verify_mode = ssl.CERT_REQUIRED
			connect_args["ssl"] = ctx
		
		_engine = create_async_engine(
			settings.database_url,
			echo=settings.database_echo,
			pool_pre_ping=True,
			pool_size=settings.database_pool_size,
			connect_args=connect_args,
		)
		
		logger.info("Async engine created!")
		
	return _engine

def get_session_factory() -> async_sessionmaker[AsyncSession]:
	
	global _session_factory
	if _session_factory is None:
		engine = get_engine()
		_session_factory = async_sessionmaker(
			engine,
			class_=AsyncSession,
   			expire_on_commit=False,
			autoflush=False
		)
	logger.debug("Async session factory created!")
	
	return _session_factory

async def get_db() -> AsyncGenerator[AsyncSession, None]:
	"""
	fastAPI dependency: generate an async session per request
	"""
	factory = get_session_factory()
	async with factory() as session:
		try:
			yield session
			await session.commit()
		except Exception:
			await session.rollback()
			raise

async def ping_db() -> bool:
	"""lightweight connectivty check"""
	engine = get_engine()
	try:
		async with engine.connect() as conn:
			await conn.execute(text("SELECT 1"))
			return True
	except Exception:
			return False

def _parse_database_url(url: str) -> dict[str, str]:
	parsed = urlparse(url)
	return {
		"user": parsed.username or "user",
		"password": parsed.password or "dev123",
		"host": parsed.hostname or "localhost",
		"port": str(parsed.port or 5432),
		"database": parsed.path.lstrip("/") if parsed.path else "pcg_data"
	}
	

async def _create_user_if_not_exists() -> bool:
	
	db_config = _parse_database_url(settings.database_url)
	target_user = db_config["user"]
	target_password = db_config["password"]
 
	system_user = os.environ.get("USER", "postgres")
	postgres_url = f"postgres+asyncpg://{system_user}@localhost:5432/postgres"
	
	logger.info(f"Checking if user '{target_user}' exists...")
	
	try:
		temp_engine = create_async_engine(
			postgres_url, 
			isolation_level="AUTOCOMMIT",
			echo=settings.database_echo
		)

		async with temp_engine.connect() as conn:
			result = await conn.execute(text(
				f"SELECT 1 FROM pg_roles WHERE rolname = '{target_user}'"
			))
			exists = result.scalar() is not None
			
			if not exists:
				await conn.execute(text(
					f"CREATE USER {target_user} WITH PASSWORD '{target_password}' CREATEDB "
				))
				logger.info(
					f"\n{'=' * 80}\n"
	 				f"DATABASE USER CREATED"
					f"Successfully user created: '{target_user}'"
				)
				await temp_engine.dispose()
				return True
			else:
				logger.info(f"User '{target_user}' already exist")
				await temp_engine.dispose()
				return False
	
	except Exception as e:
		logger.warning(
			f"Failed to create databaseuser: {e}"
		)
		return False

async def _create_database_if_not_exists() -> bool:
	"""
	Attempt to create the database if it doesn't exist.
	Connects to 'postgres' database first, then creates target database.
	Returns True if database was created, False otherwise.
	"""
	db_config = _parse_database_url(settings.database_url)
	target_db = db_config["database"]

	# Build connection URL to 'postgres' database (default)
	postgres_url = settings.database_url.replace(f"/{target_db}", "/postgres")

	logger.info(f"Attempting to create database '{target_db}'...")

	try:
		# Create temporary engine connected to postgres database
		temp_engine = create_async_engine(
			postgres_url,
			isolation_level="AUTOCOMMIT",
			echo=settings.database_echo,
		)

		async with temp_engine.connect() as conn:
			# Check if database exists
			result = await conn.execute(
				text(f"SELECT 1 FROM pg_database WHERE datname = '{target_db}'")
			)
			exists = result.scalar() is not None

			if not exists:
				# Create database
				await conn.execute(text(f"CREATE DATABASE {target_db}"))
				logger.info(
					f"\n{'=' * 80}\n"
					f"✓ DATABASE CREATED\n"
					f"{'=' * 80}\n"
					f"Successfully created database: {target_db}\n"
					f"{'=' * 80}\n"
				)
				await temp_engine.dispose()
				return True
			else:
				logger.info(f"Database '{target_db}' already exists")
				await temp_engine.dispose()
				return False

	except Exception as e:
		logger.error(f"Failed to create database: {e}")
		return False

async def init_db() -> None:
    """
    Called on app startup:
    - Verifies connection
    - Creates database if it doesn't exist (local only)
    - Creates tables if they don't exist
    """
    # Import here to avoid circular imports with models
    # from app.models.base import Base

    is_local = settings.environment in ("local", "dev")

    try:
        logger.info("Checking database connection...")
        engine = get_engine()
        db_config = _parse_database_url(settings.database_url)

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info(
                f"\n{'=' * 80}\n"
                f"✓ DATABASE CONNECTION SUCCESSFUL\n"
                f"{'=' * 80}\n"
                f"Connected to PostgreSQL:\n"
                f"  Host:     {db_config['host']}\n"
                f"  Port:     {db_config['port']}\n"
                f"  Database: {db_config['database']}\n"
                f"  User:     {db_config['user']}\n"
                f"{'=' * 80}\n"
            )

        # Note: Table creation is handled by Alembic migrations
        # Uncomment the following lines only if you need auto-creation in local dev
        # logger.info("Creating database tables if they don't exist...")
        # async with engine.begin() as conn:
        #     await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialization complete")

    except (ConnectionRefusedError, OSError):
        # Database connection refused
        db_config = _parse_database_url(settings.database_url)

        logger.error(
            f"\n{'=' * 80}\n"
            f"DATABASE CONNECTION FAILED\n"
            f"{'=' * 80}\n"
            f"Could not connect to PostgreSQL at: {settings.database_url}\n\n"
            f"Connection details:\n"
            f"  Host:     {db_config['host']}\n"
            f"  Port:     {db_config['port']}\n"
            f"  Database: {db_config['database']}\n"
            f"  User:     {db_config['user']}\n\n"
            f"Please ensure:\n"
            f"  1. PostgreSQL is installed and running\n"
            f"  2. PostgreSQL is listening on {db_config['host']}:{db_config['port']}\n"
            f"{'=' * 80}\n"
        )
        raise

    except Exception as e:
        # Reset engine for reconnection attempts
        global _engine, _session_factory

        # Only auto-create database/user in local/dev environments
        error_msg = str(e).lower()

        if not is_local:
            # Production: Don't auto-create, fail fast
            logger.error(
                f"Database initialization failed in {settings.environment} environment. "
                f"Auto-creation is disabled. Please verify your RDS configuration."
            )
            raise

        # Local/Dev: Try to auto-create user/database
        if "role" in error_msg and "does not exist" in error_msg:
            logger.warning("Database user does not exist, attempting to create it...")

            # Reset engine since we need to reconnect
            if _engine is not None:
                await _engine.dispose()
                _engine = None
            _session_factory = None

            # Try to create the user
            user_created = await _create_user_if_not_exists()

            if user_created:
                # Retry initialization with new user
                logger.info("Retrying database initialization...")
                await init_db()
                return
            else:
                logger.error("Failed to create database user automatically")
                raise

        # Check if it's a database-not-found error
        elif "database" in error_msg and (
            "does not exist" in error_msg or "not exist" in error_msg
        ):
            logger.warning("Database does not exist, attempting to create it...")

            # Reset engine since we need to reconnect
            if _engine is not None:
                await _engine.dispose()
                _engine = None
            _session_factory = None

            # Try to create the database
            created = await _create_database_if_not_exists()

            if created:
                # Retry initialization with new database
                logger.info("Retrying database initialization...")
                await init_db()
                return
            else:
                logger.error("Failed to create database automatically")
                raise
        else:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            raise


async def close_engine() -> None:
    """Called on app shutdown to dispose engine and reset factory."""
    global _engine, _session_factory

    if _engine is not None:
        await _engine.dispose()
        _engine = None
        logger.debug("Async engine disposed")

    _session_factory = None
    logger.debug("Session factory reset")


def reset_session_factory() -> None:
    """Manual reset if you ever need to rotate the engine."""
    global _session_factory
    _session_factory = None
