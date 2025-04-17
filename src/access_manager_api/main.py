import logging

from fastapi import FastAPI

from access_manager_api.app_context import init_access_manager_id
from access_manager_api.config import settings
from access_manager_api.routes import router
from access_manager_api.services.access_guard import get_access_guard_enforcer
from access_manager_api.services.db import init_db, get_db

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
    init_db(settings.database_url)
    logger.info("Database initialized")

    init_access_manager_id(next(get_db()))

    # Initialize access guard service
    get_access_guard_enforcer()
    logger.info("Permissions service initialized")
    
    logger.info("Application startup completed")
