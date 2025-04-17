from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from access_manager_api.models.base import Base

class Org(Base):
    __tablename__ = 'orgs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    
    # Relationships
    users = relationship("User", back_populates="org")
    org_apps = relationship("OrgApps", back_populates="org")