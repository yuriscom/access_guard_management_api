from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from access_manager_api.models.base import Base


class IAMRolePolicy(Base):
    __tablename__ = 'iam_role_policies'

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey('iam_roles.id', ondelete='CASCADE'), nullable=False)
    permission_id = Column(Integer, ForeignKey('iam_permissions.id', ondelete='CASCADE'), nullable=False)
    effect = Column(String, nullable=False, default="allow")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    role = relationship("IAMRole", back_populates="role_policies")
    permission = relationship("IAMPermission", back_populates="role_policies")