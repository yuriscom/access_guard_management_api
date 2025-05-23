from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, mapped_column
from access_manager_api.models.base import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid

class IAMUserRole(Base):
    __tablename__ = 'iam_user_roles'

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey('iam_roles.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="roles")
    role = relationship("IAMRole", back_populates="user_roles") 