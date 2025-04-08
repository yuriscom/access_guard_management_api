from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Text, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base
from .enums import Scope

class IAMRole(Base):
    __tablename__ = 'iam_roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    scope = Column(Enum(Scope), nullable=False)
    app_id = Column(Integer, ForeignKey('apps.id', ondelete='CASCADE'), nullable=True)
    role_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    app = relationship("App", back_populates="roles")
    role_policies = relationship("IAMRolePolicy", back_populates="role")
    user_roles = relationship("UserRole", back_populates="role")

    __table_args__ = (
        UniqueConstraint('scope', 'app_id', 'role_name', name='uix_scope_app_role'),
    )

    def get_policy_object(self) -> str:
        """
        Returns the policy object string representation for this resource.
        Format: {scope_name}:{app_id}:{resource_name}
        """
        return f"{self.scope.name}:{self.app_id}:{self.role_name}"