from typing import List, Optional

from sqlalchemy.orm import Session

from access_manager_api.models import IAMRolePolicy
from access_manager_api.schemas import IAMRolePolicyCreate


class IAMRolePolicyService:
    def __init__(self, db: Session):
        self.db = db

    def create_policy(self, policy: IAMRolePolicyCreate) -> IAMRolePolicy:
        db_policy = IAMRolePolicy(**policy.model_dump())
        self.db.add(db_policy)
        self.db.commit()
        self.db.refresh(db_policy)
        return db_policy

    def get_policy(self, policy_id: int) -> Optional[IAMRolePolicy]:
        return self.db.query(IAMRolePolicy).filter(IAMRolePolicy.id == policy_id).first()

    def get_policies(self, skip: int = 0, limit: int = 100) -> List[IAMRolePolicy]:
        return self.db.query(IAMRolePolicy).offset(skip).limit(limit).all()

    def get_policies_by_role(self, role_id: int) -> List[IAMRolePolicy]:
        return self.db.query(IAMRolePolicy).filter(IAMRolePolicy.role_id == role_id).all()

    def update_policy(self, policy_id: int, policy: IAMRolePolicyCreate) -> Optional[IAMRolePolicy]:
        db_policy = self.get_policy(policy_id)
        if db_policy:
            for key, value in policy.model_dump().items():
                setattr(db_policy, key, value)
            self.db.commit()
            self.db.refresh(db_policy)
        return db_policy

    def delete_policy(self, policy_id: int) -> bool:
        db_policy = self.get_policy(policy_id)
        if db_policy:
            self.db.delete(db_policy)
            self.db.commit()
            return True
        return False
