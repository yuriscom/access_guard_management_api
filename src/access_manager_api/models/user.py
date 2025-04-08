from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    org_id = Column(Integer, ForeignKey('orgs.id', ondelete='CASCADE'), nullable=False)
    
    # Relationships
    org = relationship("Org", back_populates="users")
    roles = relationship("UserRole", back_populates="user")
    user_policies = relationship("IAMUserPolicy", back_populates="user")