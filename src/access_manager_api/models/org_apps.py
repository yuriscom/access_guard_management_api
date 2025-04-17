from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class OrgApps(Base):
    __tablename__ = 'org_apps'

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(Integer, ForeignKey('orgs.id', ondelete='CASCADE'), nullable=False)
    app_id = Column(Integer, ForeignKey('apps.id', ondelete='CASCADE'), nullable=False)


    # Relationships
    org = relationship("Org", back_populates="org_apps")
    app = relationship("App", back_populates="org_apps")