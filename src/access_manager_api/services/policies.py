from access_guard.authz.factory import get_permissions_enforcer
from access_guard.authz.models.enums import PolicyLoaderType
from access_guard.authz.models.permissions_enforcer_params import PermissionsEnforcerParams
from fastapi import Depends
from sqlalchemy.orm import Session

from access_manager_api.config import settings
from access_manager_api.providers.policy_query_provider import AccessManagementQueryProvider
from access_manager_api.schemas.policies import PoliciesParams
from access_manager_api.services.db import get_db


class PoliciesService:
    def __init__(self, db: Session):
        self.db = db

    def get_policies(self, policiesParams: PoliciesParams):
        params_dict = {
            **settings.model_dump(),  # static settings from config
            "policy_loader_type": PolicyLoaderType.DB,
            "filter": {
                "policy_api_scope": policiesParams.scope,
                "policy_api_appid": str(policiesParams.app_id) if policiesParams.app_id is not None else None,
                "policy_api_userid": str(policiesParams.user_id) if policiesParams.user_id is not None else None,
            }
        }

        enforcer_settings = PermissionsEnforcerParams(**params_dict);

        enforcer = get_permissions_enforcer(
            settings=enforcer_settings,
            engine=self.db.bind,
            new_instance=True,
            query_provider=AccessManagementQueryProvider()
        )

        response = {
            "resource_prefix": "",
            "policies": self._extract_policies(enforcer)
        }

        if policiesParams.scope and policiesParams.app_id:
            response["resource_prefix"] = f"{policiesParams.scope}/{policiesParams.app_id}/"

        return response

    def _extract_policies(self, enforcer) -> list:
        policies = []

        for sec in ["p", "g"]:
            for ptype, ast in enforcer._model.model.get(sec, {}).items():
                for rule in ast.policy:
                    policies.append({
                        "ptype": ptype,
                        "subject": rule[0] if len(rule) > 0 else None,
                        "object": rule[1] if len(rule) > 1 else None,
                        "action": rule[2] if len(rule) > 2 else None,
                        "effect": rule[3] if len(rule) > 3 else None,
                    })

        return policies


def get_policies_service(db: Session = Depends(get_db)):
    return PoliciesService(db)
