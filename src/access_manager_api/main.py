import logging

from fastapi import FastAPI

from .routes import router
from .services.iam import get_access_guard_service

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
    # start access guard
    get_access_guard_service()
    logger.info("Permissions service initialized")
