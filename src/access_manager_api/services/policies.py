from typing import Optional

from access_guard.authz.factory import get_permissions_enforcer
from access_guard.authz.loaders.policy_code_loader import PolicyCodeLoader
from access_guard.authz.loaders.policy_db_loader import PolicyDbLoader
from access_guard.authz.models.permissions_enforcer_params import PermissionsEnforcerParams
from fastapi import Depends
from sqlalchemy.orm import Session

from access_manager_api.infra.database import get_db
from access_manager_api.providers.policy_query_provider import AccessManagementQueryProvider
from access_manager_api.providers.synthetic_policies_applications_provider import SyntheticAppPoliciesProvider
from access_manager_api.schemas.policies import PoliciesParams


class PoliciesService:
    def __init__(self, db: Session):
        self.db = db

    def get_policies(self, policiesParams: PoliciesParams):
        policy_loaders = [
            PolicyDbLoader(AccessManagementQueryProvider(), self.db.bind),
        ]
        if policiesParams.app_id:
            policy_loaders.append(PolicyCodeLoader(policy_provider=SyntheticAppPoliciesProvider(self.db)))

        params_dict = {
            "filter": {
                "policy_api_scope": policiesParams.scope,
                "policy_api_appid": str(policiesParams.app_id) if policiesParams.app_id is not None else None,
                "policy_api_userid": str(policiesParams.user_id) if policiesParams.user_id is not None else None,
            }
        }

        enforcer_settings = PermissionsEnforcerParams(**params_dict);

        enforcer = get_permissions_enforcer(
            settings=enforcer_settings,
            new_instance=True,
            policy_loaders=policy_loaders
        )

        resource_prefix = f"{policiesParams.scope}/{policiesParams.app_id}/"

        response = {
            "resource_prefix": "",
            "policies": self._extract_policies(enforcer, resource_prefix)
        }

        if policiesParams.scope and policiesParams.app_id:
            response["resource_prefix"] = resource_prefix

        return response

    def _extract_policies(self, enforcer, resource_prefix="") -> list:
        policies = []

        def strip_prefix(value: Optional[str]) -> Optional[str]:
            if value and resource_prefix and value.startswith(resource_prefix):
                return value[len(resource_prefix):]
            return value

        for sec in ["p", "g"]:
            for ptype, ast in enforcer._model.model.get(sec, {}).items():
                for rule in ast.policy:
                    _subject = rule[0] if len(rule) > 0 else None
                    _object = rule[1] if len(rule) > 1 else None
                    _action = rule[2] if len(rule) > 2 else None
                    _effect = rule[3] if len(rule) > 3 else None

                    stripped_subject = strip_prefix(_subject)
                    stripped_object = strip_prefix(_object)

                    _description = None
                    if ptype == "p":
                        _description = f"{_effect} {_action} access for {stripped_subject} to resource {stripped_object}"
                    elif ptype == "g":
                        _description = f"assign {stripped_subject} to role {stripped_object}"

                    policies.append({
                        "ptype": ptype,
                        "subject": _subject,
                        "object": _object,
                        "action": _action,
                        "effect": _effect,
                        "description": _description
                    })

        return policies


def get_policies_service(db: Session = Depends(get_db)):
    return PoliciesService(db)
