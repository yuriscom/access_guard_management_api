-- Rename the table
ALTER TABLE iam_user_policies RENAME TO iam_user_permissions;

-- Rename the primary key constraint
ALTER INDEX iam_user_policies_pkey RENAME TO iam_user_permissions_pkey;

-- Rename the effect check constraint
ALTER TABLE iam_user_permissions RENAME CONSTRAINT iam_user_policies_effect_check TO iam_user_permissions_effect_check;

-- Rename the unique index
ALTER INDEX uix_user_permission_iam_user_policies RENAME TO uix_user_permission_iam_user_permissions;

-- Rename foreign key constraints
ALTER TABLE iam_user_permissions RENAME CONSTRAINT iam_policies_user_id_fkey TO iam_user_permissions_user_id_fkey;
ALTER TABLE iam_user_permissions RENAME CONSTRAINT iam_user_policies_permission_id_fkey TO iam_user_permissions_permission_id_fkey;
