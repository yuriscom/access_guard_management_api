import logging

from fastapi import FastAPI

from .routes import router
from .services.access_guard import get_access_guard_enforcer
from .config import settings
from .services.db import init_db

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Access Manager API",
    description="API for managing access policies and permissions",
    version="1.0.0"
)

# Include all routes
app.include_router(router)


# Initialize permissions service
@app.on_event("startup")
async def startup_event():
    # Initialize database
    engine = init_db(settings.database_url)
    logger.info("Database initialized")
    
    # Initialize access guard service
    get_access_guard_enforcer()
    logger.info("Permissions service initialized")
    
    logger.info("Application startup completed")
