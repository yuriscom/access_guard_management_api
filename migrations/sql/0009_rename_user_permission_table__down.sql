-- Rename the table back
ALTER TABLE iam_user_permissions RENAME TO iam_user_policies;

-- Rename the primary key constraint back
ALTER INDEX iam_user_permissions_pkey RENAME TO iam_user_policies_pkey;

-- Rename the effect check constraint back
ALTER TABLE iam_user_policies RENAME CONSTRAINT iam_user_permissions_effect_check TO iam_user_policies_effect_check;

-- Rename the unique index back
ALTER INDEX uix_user_permission_iam_user_permissions RENAME TO uix_user_permission_iam_user_policies;

-- Rename foreign key constraints back
ALTER TABLE iam_user_policies RENAME CONSTRAINT iam_user_permissions_user_id_fkey TO iam_policies_user_id_fkey;
ALTER TABLE iam_user_policies RENAME CONSTRAINT iam_user_permissions_permission_id_fkey TO iam_user_policies_permission_id_fkey;
