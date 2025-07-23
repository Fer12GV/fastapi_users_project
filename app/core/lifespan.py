from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from app.db.database import engine
from app.models import user
from app.core.config import settings

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI application.
    Manages startup and shutdown events.
    """
    # STARTUP EVENTS
    logger.info("🚀 Starting FastAPI Users API...")
    
    try:
        # Create database tables
        async with engine.begin() as conn:
            await conn.run_sync(user.Base.metadata.create_all)
        logger.info("✅ Database tables created successfully")
        
        # Initialize any other startup tasks here
        logger.info(f"🌟 Application '{settings.APP_NAME}' started successfully")
        logger.info(f"🔧 Debug mode: {settings.DEBUG}")
        logger.info(f"🔐 JWT expiration: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        raise
    
    # APPLICATION IS RUNNING
    yield
    
    # SHUTDOWN EVENTS
    logger.info("🛑 Shutting down FastAPI Users API...")
    
    try:
        # Close database connections
        await engine.dispose()
        logger.info("✅ Database connections closed")
        
        # Cleanup any other resources here
        logger.info("🏁 Application shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")
        raise
