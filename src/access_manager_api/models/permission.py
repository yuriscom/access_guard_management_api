import uuid

from sqlalchemy import Column, String, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, mapped_column

from access_manager_api.models.base import Base


class IAMPermission(Base):
    __tablename__ = 'iam_permissions'
    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey('iam_resources.id', ondelete='CASCADE'), nullable=False)
    action = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    resource = relationship("IAMResource", back_populates="permissions")
    role_permissions = relationship("IAMRolePermission", back_populates="permission")
    user_permissions = relationship("IAMUserPermission", back_populates="permission")

    __table_args__ = (
        UniqueConstraint('resource_id', 'action', name='uix_resource_action'),
    )
