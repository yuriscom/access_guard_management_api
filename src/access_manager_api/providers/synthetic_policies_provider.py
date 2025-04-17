from collections import defaultdict
from typing import List, Tuple

from sqlalchemy.orm import Session

from access_manager_api import constants
from access_manager_api.app_context import get_access_manager_app_id
from access_manager_api.models import IAMRole, UserRole, User, Scope, App, Org, OrgApps


def load_synthetic_policies(session: Session) -> List[Tuple[str, ...]]:
    policies = []

    policies += get_policies_from_synthetic_roles(session)
    # policies += get_policies_from_synthetic_resources(session)
    # policies += get_policies_for_special_cases(session)

    return policies

# def load_smc_superadmin_policies(session: Session) -> List[Tuple[str, ...]]:
#     # Get superadmin role
#     role = session.query(IAMRole).filter_by(scope=Scope.SMC.name, role_name=PoliciesConstants.superadmin).first()
#     if not role:
#         return []
#
#     # Query users with superadmin role
#     users = (
#         session.query(User)
#         .join(UserRole, User.id == UserRole.user_id)
#         .filter(UserRole.role_id == role.id)
#         .all()
#     )
#
#     # Create policies for each superadmin user
#     return [
#         ("p", str(user.id), f"{Scope.SMC.name}/*", "*", "allow")
#         for user in users
#     ]

def get_policies_from_synthetic_roles(db: Session):
    UserModel = User
    OrgModel = Org
    OrgAppModel = OrgApps
    AppModel = App
    UserRoleModel = UserRole
    IAMRoleModel = IAMRole

    access_manager_api_id = get_access_manager_app_id()

    query = (
        db.query(UserModel.id.label("user_id"),
                 AppModel.id.label("app_id"),
                 IAMRoleModel.role_name,
                 IAMRoleModel.synthetic_pattern
                 )
        .join(OrgModel, UserModel.org_id == OrgModel.id)
        .join(OrgAppModel, OrgModel.id == OrgAppModel.org_id)
        .join(AppModel, AppModel.id == OrgAppModel.app_id)
        .join(UserRoleModel, UserRoleModel.user_id == UserModel.id)
        .join(IAMRoleModel, IAMRoleModel.id == UserRoleModel.role_id)
        .filter(
            IAMRoleModel.scope == Scope.SMC.name,
            IAMRoleModel.app_id == access_manager_api_id,
            IAMRoleModel.synthetic == True
        )
    )

    rows = query.all()
    policies: List[Tuple[str, ...]] = []
    # 2. Group users by (role_name, app_id, pattern)
    grouped: defaultdict[Tuple[str, int, str], List[int]] = defaultdict(list)
    for row in rows:
        key = (row.role_name, row.app_id, row.synthetic_pattern)
        grouped[key].append(row.user_id)

    # 3. Generate policies
    for (role_name, app_id, pattern), user_ids in grouped.items():
        role_subject = f"{Scope.SMC.name}/{access_manager_api_id}/{role_name}/{Scope.APP.name}/{app_id}"
        resource = role_subject
        if pattern:
            resolved_path = pattern.replace("{app_id}", str(app_id))
            resource = f"{Scope.SMC.name}/{access_manager_api_id}/{resolved_path}"

        if role_name == constants.ROLE_IAM_MANAGER:
            actions = ["read", "write"]
        elif role_name == constants.ROLE_POLICY_READER:
            actions = ["read"]
        elif role_name == constants.ROLE_AM_ADMIN:
            resource = f"{Scope.SMC.name}/{access_manager_api_id}/*"
            actions = ["*"]
        elif role_name == constants.ROLE_SUPERADMIN:
            resource = f"{Scope.SMC.name}/*"
            actions = ["*"]

        for action in actions:
            policies.append(("p", role_subject, resource, action, "allow"))

        for user_id in user_ids:
            policies.append(("g", str(user_id), role_subject))

    return policies

    #
    # policies = []
    # for row in rows:
    #     role = row.role_name
    #     user_id = str(row.user_id)
    #     app_id = row.app_id
    #
    #     iam_res = f"SMC/{access_manager_api_id}/iam/APP/{app_id}"
    #     policies_res = f"SMC/{access_manager_api_id}/policies/APP/{app_id}"
    #
    #     if role == "IAMManager":
    #         policies.append(("p", user_id, iam_res, "read", "allow"))
    #         policies.append(("p", user_id, iam_res, "write", "allow"))
    #     elif role == "PolicyReader":
    #         policies.append(("p", user_id, policies_res, "read", "allow"))
    #     elif role == "Superadmin":
    #         policies.append(("p", user_id, f"SMC/{access_manager_api_id}/*", "*", "allow"))
    #
    # return policies