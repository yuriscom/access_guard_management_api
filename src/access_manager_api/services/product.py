from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from access_manager_api.infra.constants import ROLE_POLICY_READER, ROLE_PRODUCT_OWNER
from access_manager_api.infra.error_handling import AlreadyExistsException
from access_manager_api.models import User, Scope
from access_manager_api.schemas import IAMRoleCreate
from access_manager_api.schemas.product import ProductOnboard
from access_manager_api.services import IAMUserRolesService
from access_manager_api.services.role import IAMRoleService


async def onboard_product(db: Session, app_id: UUID, request: ProductOnboard, initiated_by: User):
    role_service = IAMRoleService(db)
    user_role_service = IAMUserRolesService(db)

    # Product Owner role
    product_owner_role = IAMRoleCreate(
        role_name=ROLE_PRODUCT_OWNER,
        app_id=app_id,
        scope=Scope.APP
    )

    # Policy Reader role
    policy_reader_role = IAMRoleCreate(
        role_name=ROLE_POLICY_READER,
        app_id=app_id,
        scope=Scope.APP
    )

    try:

        try:
            created_product_owner_role = await role_service.create_role(product_owner_role, commit=False)
        except IntegrityError:
            raise AlreadyExistsException(f"{ROLE_PRODUCT_OWNER} role already exists for app {app_id}")

        try:
            await user_role_service.assign_user_to_role(request.product_owner_id, created_product_owner_role.id, commit=False)
        except IntegrityError:
            raise AlreadyExistsException(f"User {request.product_owner_id} is already assigned to {ROLE_PRODUCT_OWNER}")

        try:
            created_policy_reader_role = await role_service.create_role(policy_reader_role, commit=False)
        except IntegrityError:
            raise AlreadyExistsException(f"{ROLE_POLICY_READER} role already exists for app {app_id}")

        # audit_log(db, action="product_onboard_assign_product_owner", user_id=initiated_by, app_id=app_id)

        try:
            await user_role_service.assign_user_to_role(request.system_user_id,
                                                        created_policy_reader_role.id,
                                                        commit=False)
        except IntegrityError:
            raise AlreadyExistsException(f"User {request.system_user_id} is already assigned to {ROLE_POLICY_READER}")

        # audit_log(db, action="product_onboard_assign_policy_reader", user_id=initiated_by, app_id=app_id)
        db.commit()
        db.refresh(created_product_owner_role)
        db.refresh(created_policy_reader_role)
    except AlreadyExistsException as e:
        db.rollback()
        print(f"Onboarding failed. System said: {e}")
        raise e  # safe to propagate
    except Exception as e:
        db.rollback()
        print(f"Unhandled error: {e}")
        raise
