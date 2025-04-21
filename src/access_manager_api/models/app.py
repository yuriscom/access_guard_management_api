import uuid

from sqlalchemy import String, Uuid, JSON
from sqlalchemy.orm import relationship, mapped_column

from access_manager_api.models.base import Base


class App(Base):
    __tablename__ = 'apps'

    id = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name = mapped_column(String, unique=True, index=True)
    roles = mapped_column(JSON, nullable=True)

    
    # Relationships
    resources = relationship("IAMResource", back_populates="app")
    roles = relationship("IAMRole", back_populates="app")
    org_apps = relationship("OrgApps", back_populates="app")