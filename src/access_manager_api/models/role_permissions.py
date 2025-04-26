from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from access_manager_api.models.base import Base


class IAMRolePermission(Base):
    __tablename__ = 'iam_role_permissions'

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), ForeignKey('iam_roles.id', ondelete='CASCADE'), nullable=False)
    permission_id = Column(UUID(as_uuid=True), ForeignKey('iam_permissions.id', ondelete='CASCADE'), nullable=False)
    effect = Column(String, nullable=False, default="allow")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    role = relationship("IAMRole", back_populates="role_permissions")
    permission = relationship("IAMPermission", back_populates="role_permissions")