from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

ACCESS_MANAGER_APP_NAME = "Access Manager"

#ENVS
ENV_LOCAL = "local"
ENV_DEMO = "demo"
ENV_DEV = "dev"
ENV_STAGING = "staging"
ENV_PROD = "prod"

# ROLES
ROLE_SUPERADMIN = "Superadmin"
ROLE_AM_ADMIN = "AMAdmin"
ROLE_POLICY_READER = "PolicyReader"
ROLE_IAM_MANAGER = "IAMManager"
ROLE_ORG_ADMIN = "OrgAdmin"
ROLE_BILLING_VIEWER = "BillingViewer"
ROLE_REPORTING_USER = "ReportingUser"
ROLE_USER_ADMIN = "admin"

## Models
APP_MODE_PUBLIC = "public"
APP_USER_MANAGEMENT_TYPE_FULLY = "fully"