import logging

from access_manager_api.infra.access_guard import get_access_guard_enforcer
from access_manager_api.infra.app_context import init_access_manager_id
from access_manager_api.infra.config import settings
from access_manager_api.infra.database import init_db, get_db
from access_manager_api.infra.error_handling import ErrorHandlerMiddleware
from access_manager_api.routes import router
from fastapi import FastAPI

logging.basicConfig(
    level=logging.DEBUG,  # or DEBUG, WARNING, etc.
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Access Manager API",
    description="API for managing access policies and permissions",
    version="1.0.0"
)

app.add_middleware(ErrorHandlerMiddleware)
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    # # disable alembic - the migrations for this db are controlled from the core ms
    # subprocess.run(["alembic", "upgrade", "head"], check=True)

    # Initialize database
    init_db(settings.CoreDB.URI)
    logger.info("Database initialized")

    # set access manager app id
    init_access_manager_id(next(get_db()))

    # Initialize access guard service
    get_access_guard_enforcer()
    logger.info("Permissions service initialized")


@app.get("/status/live", include_in_schema=False)
def get_status_live():
    return {"message": "OK"}


@app.get("/status/ready", include_in_schema=False)
def get_status_ready():
    return {"message": "OK"}
