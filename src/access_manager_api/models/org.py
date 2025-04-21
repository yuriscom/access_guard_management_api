from sqlalchemy import Column, UUID, DateTime
from sqlalchemy.orm import relationship

from access_manager_api.models.base import Base


class Org(Base):
    __tablename__ = 'orgs'

    id = Column(UUID(as_uuid=True), primary_key=True)
    org_id = Column(UUID(as_uuid=True), nullable=False)
    app_id = Column(UUID(as_uuid=True), nullable=False)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="org")
    org_apps = relationship("OrgApps", back_populates="org")