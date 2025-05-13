-- ######### ROLE TABLE ########## --

-- Revert iam_roles scope constraint
ALTER TABLE iam_roles DROP CONSTRAINT IF EXISTS iam_roles_scope_check;

ALTER TABLE iam_roles
  ADD CONSTRAINT iam_roles_scope_check CHECK (
    scope IN ('SMC', 'PRODUCT', 'APP')
  );

-- Drop new index on iam_roles
DROP INDEX IF EXISTS uix_scope_app_org_role;

-- Restore original unique index on iam_roles
CREATE UNIQUE INDEX uix_scope_app_role
  ON public.iam_roles (
    scope,
    COALESCE(app_id, '00000000-0000-0000-0000-000000000000'::uuid),
    role_name
  );

-- Remove org_id from iam_roles
ALTER TABLE iam_roles DROP COLUMN IF EXISTS org_id;


-- ######### RESOURCE TABLE ########## --

-- Revert iam_resources scope constraint
ALTER TABLE iam_resources DROP CONSTRAINT IF EXISTS iam_resources_scope_check;

ALTER TABLE iam_resources
  ADD CONSTRAINT iam_resources_scope_check CHECK (
    scope IN ('SMC', 'PRODUCT', 'APP')
  );

-- Drop new index on iam_resources
DROP INDEX IF EXISTS uix_scope_app_org_resource;

-- Restore original unique index on iam_resources
CREATE UNIQUE INDEX uix_scope_app_resource
  ON public.iam_resources (
    scope,
    COALESCE(app_id, '00000000-0000-0000-0000-000000000000'::uuid),
    resource_name
  );

-- Remove org_id from iam_resources
ALTER TABLE iam_resources DROP COLUMN IF EXISTS org_id;
