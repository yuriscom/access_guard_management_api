from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class PolicyWebhook(Base):
    __tablename__ = "iam_policy_refresh_hooks"

    id = Column(Integer, primary_key=True, index=True)
    scope = Column(String(64), nullable=False)
    app_id = Column(Integer, nullable=False)
    url = Column(String, nullable=False)
    secret = Column(String, nullable=False)  # Encrypted + Base64 string
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())

    __table_args__ = (
        Index("ix_iam_hooks_scope_app_id", "scope", "app_id"),
    )
