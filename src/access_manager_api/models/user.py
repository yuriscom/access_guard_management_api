from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import String, ForeignKey, Uuid, Boolean, DateTime
from sqlalchemy.orm import relationship, mapped_column

from access_manager_api.models.base import Base


class User(Base):
    __tablename__ = 'users'

    id = mapped_column(Uuid, primary_key=True, default=uuid4)
    email = mapped_column(String, nullable=False, unique=True)
    org_id = mapped_column(Uuid, ForeignKey("orgs.id"))
    role = mapped_column(String, nullable=True)
    is_super_admin = mapped_column(Boolean, nullable=False, default=False)
    
    # Relationships
    org = relationship("Org", back_populates="users")
    roles = relationship("UserRole", back_populates="user")
    user_policies = relationship("IAMUserPolicy", back_populates="user")