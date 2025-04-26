import logging
from typing import List
from uuid import UUID

import httpx
from sqlalchemy.orm import Session

from access_manager_api.models import Scope
from access_manager_api.models.policy_webhook import PolicyWebhook

logger = logging.getLogger(__name__)


async def send_policy_refresh_webhook(scope: Scope, app_id: UUID, db: Session):
    hooks: List[PolicyWebhook] = (
        db.query(PolicyWebhook)
            .filter_by(scope=scope.name, app_id=app_id, is_active=True)
            .all()
    )

    async with httpx.AsyncClient(timeout=5.0) as client:
        for hook in hooks:
            try:
                # secret = decrypt_secret(hook.secret_encrypted)
                secret = hook.secret
                headers = {
                    "Authorization": f"Bearer {secret}"
                }
                await client.post(hook.url, headers=headers)
            except Exception as e:
                logger.warning(f"Failed to send webhook to {hook.url}: {e}")
