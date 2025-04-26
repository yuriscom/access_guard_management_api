import uuid

from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy.sql import func

from access_manager_api.models.base import Base


class IAMUserPermission(Base):
    __tablename__ = 'iam_user_permissions'

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    permission_id = Column(UUID(as_uuid=True), ForeignKey('iam_permissions.id', ondelete='CASCADE'), nullable=False)
    effect = Column(String, nullable=False, default="allow")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="user_permissions")
    permission = relationship("IAMPermission", back_populates="user_permissions")
