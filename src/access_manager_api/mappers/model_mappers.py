from access_manager_api.models import User
from access_guard.authz.models.entities import User as AccessGuardUser


def mapUserToAccessGuardUser(user: User) -> AccessGuardUser:
    return AccessGuardUser(id=user.id, name=user.email)
