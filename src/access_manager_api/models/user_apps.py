from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from access_manager_api.models.base import Base


class UserApp(Base):
    __tablename__ = "user_apps"

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    app_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_roles = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
