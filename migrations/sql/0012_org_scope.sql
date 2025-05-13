-- ######### ROLE TABLE ########## --

-- Add org_id to iam_roles
ALTER TABLE iam_roles ADD COLUMN IF NOT EXISTS org_id UUID;

-- Drop old CHECK constraint on iam_roles
ALTER TABLE iam_roles DROP CONSTRAINT IF EXISTS iam_roles_scope_check;

-- Add updated CHECK constraint
ALTER TABLE iam_roles
  ADD CONSTRAINT iam_roles_scope_check CHECK (
    scope IN ('SMC', 'PRODUCT', 'APP', 'ORG')
  );

-- Drop old unique index on roles
DROP INDEX IF EXISTS uix_scope_app_role;

-- Add new unique index using COALESCE for app_id and org_id
CREATE UNIQUE INDEX uix_scope_app_org_role
  ON public.iam_roles (
    scope,
    COALESCE(app_id, '00000000-0000-0000-0000-000000000000'::uuid),
    COALESCE(org_id, '00000000-0000-0000-0000-000000000000'::uuid),
    role_name
  );


-- ######### RESOURCE TABLE ########## --

-- Add org_id to iam_resources
ALTER TABLE iam_resources ADD COLUMN IF NOT EXISTS org_id UUID;

-- Drop old CHECK constraint on iam_resources
ALTER TABLE iam_resources DROP CONSTRAINT IF EXISTS iam_resources_scope_check;

-- Add updated CHECK constraint
ALTER TABLE iam_resources
  ADD CONSTRAINT iam_resources_scope_check CHECK (
    scope IN ('SMC', 'PRODUCT', 'APP', 'ORG')
  );

-- Drop old unique index on resources
DROP INDEX IF EXISTS uix_scope_app_resource;

-- Add new unique index using COALESCE for app_id and org_id
CREATE UNIQUE INDEX uix_scope_app_org_resource
  ON public.iam_resources (
    scope,
    COALESCE(app_id, '00000000-0000-0000-0000-000000000000'::uuid),
    COALESCE(org_id, '00000000-0000-0000-0000-000000000000'::uuid),
    resource_name
  );