from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class IAMUserPolicy(Base):
    __tablename__ = 'iam_user_policies'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    permission_id = Column(Integer, ForeignKey('iam_permissions.id', ondelete='CASCADE'), nullable=False)
    effect = Column(String, nullable=False, default="allow")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="user_policies")
    permission = relationship("IAMPermission", back_populates="user_policies") 