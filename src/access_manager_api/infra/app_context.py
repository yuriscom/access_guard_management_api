from typing import Optional

from sqlalchemy.orm import Session

from access_manager_api.infra.constants import ACCESS_MANAGER_APP_NAME
from access_manager_api.models.policy_webhook import PolicyWebhook

ACCESS_MANAGER_APP_ID: Optional[str] = None
HOOK_CACHE: dict[tuple[str, int], list[dict]] = {}


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


# def load_hooks_into_memory(db: Session):
#     rows = db.query(PolicyWebhook).filter_by(is_active=True).all()
#     for row in rows:
#         key = (row.scope, row.app_id)
#         HOOK_CACHE.setdefault(key, []).append({
#             "url": row.url,
#             # "secret": decrypt_secret(row.secret_encrypted),
#             "secret": row.secret,
#         })


def get_root_path() -> str:
    """Get the root path of the project."""
    from pathlib import Path
    path = Path(__file__).parent.parent.parent.parent
    return str(path.absolute())
