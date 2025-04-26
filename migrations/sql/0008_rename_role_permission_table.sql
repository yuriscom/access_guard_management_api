-- Rename the table
ALTER TABLE iam_role_policies RENAME TO iam_role_permissions;

-- Rename the primary key constraint
ALTER INDEX iam_policies_pkey RENAME TO iam_role_permissions_pkey;

-- Rename the effect check constraint
ALTER TABLE iam_role_permissions RENAME CONSTRAINT iam_policies_effect_check TO iam_role_permissions_effect_check;

-- Rename the unique index
ALTER INDEX uix_role_permission_effect_iam_role_policies RENAME TO uix_role_permission_effect_iam_role_permissions;

-- Rename foreign key constraints
ALTER TABLE iam_role_permissions RENAME CONSTRAINT iam_policies_permission_id_fkey TO iam_role_permissions_permission_id_fkey;
ALTER TABLE iam_role_permissions RENAME CONSTRAINT iam_policies_role_id_fkey TO iam_role_permissions_role_id_fkey;
