import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, Integer
from sqlalchemy import DateTime, ForeignKey, Uuid
from sqlalchemy.orm import relationship, mapped_column

from access_manager_api.models.base import Base


class OrgApps(Base):
    __tablename__ = 'org_apps'

    id = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    org_id = Column(Integer, ForeignKey('orgs.id', ondelete='CASCADE'), nullable=False)
    app_id = Column(Integer, ForeignKey('apps.id', ondelete='CASCADE'), nullable=False)
    started_at = mapped_column(DateTime, default=datetime.now(timezone.utc))

    # Relationships
    org = relationship("Org", back_populates="org_apps")
    app = relationship("App", back_populates="org_apps")
