-- Rename the table
ALTER TABLE user_roles RENAME TO iam_user_roles;

-- Rename the primary key constraint
ALTER INDEX user_roles_pkey RENAME TO iam_user_roles_pkey;

-- Rename the unique index
ALTER INDEX uix_user_role_iam_user_roles RENAME TO uix_user_role_iam_user_roles_index;

-- Rename foreign key constraints
ALTER TABLE iam_user_roles RENAME CONSTRAINT user_roles_user_id_fkey TO iam_user_roles_user_id_fkey;
ALTER TABLE iam_user_roles RENAME CONSTRAINT user_roles_role_id_fkey TO iam_user_roles_role_id_fkey;
