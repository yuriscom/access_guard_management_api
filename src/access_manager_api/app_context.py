from typing import Optional

from sqlalchemy.orm import Session

from access_manager_api.constants import ACCESS_MANAGER_APP_NAME

ACCESS_MANAGER_APP_ID: Optional[str] = None

def init_access_manager_id(db: Session):
    global ACCESS_MANAGER_APP_ID
    from access_manager_api.models import App

    app = db.query(App).filter(App.name == ACCESS_MANAGER_APP_NAME).first()
    if not app:
        raise RuntimeError(f"App with name '{ACCESS_MANAGER_APP_NAME}' not found.")
    ACCESS_MANAGER_APP_ID = str(app.id)

def get_access_manager_app_id() -> str:
    if ACCESS_MANAGER_APP_ID is None:
        raise RuntimeError("ACCESS_MANAGER_APP_ID is not initialized.")
    return ACCESS_MANAGER_APP_ID
