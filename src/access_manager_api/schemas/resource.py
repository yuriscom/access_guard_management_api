from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from access_manager_api.models.enums import Scope


class IAMResourceBase(BaseModel):
    scope: Scope
    app_id: Optional[int] = None
    resource_name: str
    description: Optional[str] = None


class IAMResourceCreate(IAMResourceBase):
    pass


class IAMResource(IAMResourceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
