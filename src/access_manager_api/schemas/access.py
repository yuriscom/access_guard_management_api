from typing import List, Dict

from pydantic import BaseModel


class Permission(BaseModel):
    action: str
    effect: str


class UserAccess(BaseModel):
    user_id: int
    user_name: str
    scope: str
    roles: List[str]
    permissions: Dict[str, List[Permission]]


class PermissionCheck(BaseModel):
    user_id: int
    resource: str
    action: str


class PermissionsList(BaseModel):
    permissions: List[str]
