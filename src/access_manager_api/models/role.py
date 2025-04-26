from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Text, Enum, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship, mapped_column
from access_manager_api.models.base import Base
from access_manager_api.models.enums import Scope
from sqlalchemy.dialects.postgresql import UUID
import uuid

class IAMRole(Base):
    __tablename__ = 'iam_roles'

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scope = Column(Enum(Scope), nullable=False)
    app_id = Column(UUID(as_uuid=True), ForeignKey('apps.id', ondelete='CASCADE'), nullable=True)
    role_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    synthetic = Column(Boolean, nullable=True)
    synthetic_pattern = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    app = relationship("App", back_populates="roles")
    role_permissions = relationship("IAMRolePermission", back_populates="role")
    user_roles = relationship("IAMUserRole", back_populates="role")

    __table_args__ = (
        UniqueConstraint('scope', 'app_id', 'role_name', name='uix_scope_app_role'),
    )

    def get_policy_object(self) -> str:
        """
        Returns the policy object string representation for this resource.
        Format: {scope_name}:{app_id}:{resource_name}
        """
        return f"{self.scope.name}:{self.app_id}:{self.role_name}"