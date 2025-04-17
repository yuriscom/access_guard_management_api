from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from access_manager_api.models.base import Base

class IAMPermission(Base):
    __tablename__ = 'iam_permissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(Integer, ForeignKey('iam_resources.id', ondelete='CASCADE'), nullable=False)
    action = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    resource = relationship("IAMResource", back_populates="permissions")
    role_policies = relationship("IAMRolePolicy", back_populates="permission")
    user_policies = relationship("IAMUserPolicy", back_populates="permission")

    __table_args__ = (
        UniqueConstraint('resource_id', 'action', name='uix_resource_action'),
    ) 