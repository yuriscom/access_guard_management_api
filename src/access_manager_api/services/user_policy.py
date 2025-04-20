from typing import List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from access_manager_api.models import IAMUserPolicy
from access_manager_api.schemas import IAMUserPolicyCreate


class IAMUserPolicyService:
    def __init__(self, db: Session):
        self.db = db

    def create_policy(self, policy: IAMUserPolicyCreate) -> IAMUserPolicy:
        db_policy = IAMUserPolicy(id=str(uuid4()), **policy.model_dump())
        self.db.add(db_policy)
        self.db.commit()
        self.db.refresh(db_policy)
        return db_policy

    def get_policy(self, policy_id: str) -> Optional[IAMUserPolicy]:
        return self.db.query(IAMUserPolicy).filter(IAMUserPolicy.id == policy_id).first()

    def get_policies(self, skip: int = 0, limit: int = 100) -> List[IAMUserPolicy]:
        return self.db.query(IAMUserPolicy).offset(skip).limit(limit).all()

    def get_policies_by_user(self, user_id: str) -> List[IAMUserPolicy]:
        return self.db.query(IAMUserPolicy).filter(IAMUserPolicy.user_id == user_id).all()

    def update_policy(self, policy_id: str, policy: IAMUserPolicyCreate) -> Optional[IAMUserPolicy]:
        db_policy = self.get_policy(policy_id)
        if db_policy:
            for key, value in policy.model_dump().items():
                setattr(db_policy, key, value)
            self.db.commit()
            self.db.refresh(db_policy)
        return db_policy

    def delete_policy(self, policy_id: str) -> bool:
        db_policy = self.get_policy(policy_id)
        if db_policy:
            self.db.delete(db_policy)
            self.db.commit()
            return True
        return False
