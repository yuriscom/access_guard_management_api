from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Text, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from access_manager_api.models.base import Base
from access_manager_api.models.enums import Scope

class IAMResource(Base):
    __tablename__ = 'iam_resources'

    id = Column(Integer, primary_key=True, autoincrement=True)
    scope = Column(Enum(Scope), nullable=False)
    app_id = Column(Integer, ForeignKey('apps.id', ondelete='CASCADE'), nullable=True)
    resource_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    app = relationship("App", back_populates="resources")
    permissions = relationship("IAMPermission", back_populates="resource")

    def get_policy_object(self) -> str:
        """
        Returns the policy object string representation for this resource.
        Format: {scope_name}:{app_id}:{resource_name}
        """
        return f"{self.scope.name}:{self.app_id}:{self.resource_name}" 