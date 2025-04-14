from typing import List, Tuple
from sqlalchemy.orm import Session
from ..models import IAMRole, UserRole, User

def load_smc_superadmin_policies(session: Session) -> List[Tuple[str, ...]]:
    # Get superadmin role
    role = session.query(IAMRole).filter_by(scope="SMC", role_name="Superadmin").first()
    if not role:
        return []

    # Query users with superadmin role
    users = (
        session.query(User)
        .join(UserRole, User.id == UserRole.user_id)
        .filter(UserRole.role_id == role.id)
        .all()
    )

    # Create policies for each superadmin user
    return [
        ("p", str(user.id), "SMC::*", "*", "allow")
        for user in users
    ]
