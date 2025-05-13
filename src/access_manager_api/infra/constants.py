from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

ACCESS_MANAGER_APP_NAME = "Access Manager"

# ENVS
ENV_LOCAL = "local"
ENV_DEMO = "demo"
ENV_DEV = "dev"
ENV_STAGING = "staging"
ENV_PROD = "prod"

# ROLES
ROLE_SUPERADMIN = "Superadmin"
ROLE_AM_ADMIN = "AMAdmin"
ROLE_IAM_MANAGER = "SMC_IAM_Manager"
ROLE_IAM_VIEWER = "SMC_IAM_Viewer"
ROLE_POLICY_READER = "SMC_IAM_Policy_Reader"
ROLE_ORG_ADMIN = "OrgAdmin"
ROLE_PRODUCT_OWNER = "ProductOwner"

# RESOURCES
RESOURCE_POLICIES = "policies"
RESOURCE_IAM = "iam"
RESOURCE_ADMIN = "*"

## Models
APP_MODE_PUBLIC = "public"
APP_USER_MANAGEMENT_TYPE_FULLY = "fully"
