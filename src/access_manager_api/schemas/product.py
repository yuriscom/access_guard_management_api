from uuid import UUID

from pydantic import BaseModel


class ProductOnboard(BaseModel):
    product_owner_id: UUID
    system_user_id: UUID
