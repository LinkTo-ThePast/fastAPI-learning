import os
import ssl
from typing import Optional
from sqlalchemy.ext.asyncio import (
  create_async_engine,
  AsyncEngine,
  AsyncSession,
  async_sessionmaker
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