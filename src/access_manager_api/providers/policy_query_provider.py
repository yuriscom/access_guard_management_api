from access_guard.authz.loaders.poicy_query_provider import PolicyQueryProvider
from pathlib import Path

def load_sql(name: str) -> str:
    with open(f"{Path(__file__).parent}/queries/{name}.sql") as f:
        return f.read()


QUERY_ALL_POLICIES = load_sql("all_policies")
QUERY_FILTERED_POLICIES = load_sql("filtered_policies")
QUERY_USER_POLICIES = load_sql("user_policies")
QUERY_ROLE_POLICIES = load_sql("role_policies")


class AccessManagementQueryProvider(PolicyQueryProvider):
    def get_all_policies_query(self):
        return QUERY_ALL_POLICIES, {}

    def get_filtered_policies_query(self, filter: dict):
        return QUERY_FILTERED_POLICIES, filter

    def get_user_policy_query(self, user_id: str):
        return QUERY_USER_POLICIES, {"user_id": user_id}

    def get_role_policy_query(self, role_id: str):
        return QUERY_ROLE_POLICIES, {"role_id": role_id}
