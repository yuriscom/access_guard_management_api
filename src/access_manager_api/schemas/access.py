import uuid
from typing import List, Dict

from pydantic import BaseModel


class Permission(BaseModel):
    action: str
    effect: str


class UserAccess(BaseModel):
    user_id: uuid.UUID
    user_email: str
    scope: str
    roles: List[str]
    permissions: Dict[str, List[Permission]]
