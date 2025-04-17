from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from access_manager_api.models.base import Base


class App(Base):
    __tablename__ = 'apps'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    resources = relationship("IAMResource", back_populates="app")
    roles = relationship("IAMRole", back_populates="app")
    org_apps = relationship("OrgApps", back_populates="app")