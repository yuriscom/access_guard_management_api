-- Rename the table back
ALTER TABLE iam_user_roles RENAME TO user_roles;

-- Rename the primary key constraint back
ALTER INDEX iam_user_roles_pkey RENAME TO user_roles_pkey;

-- Rename the unique index back
ALTER INDEX uix_user_role_iam_user_roles_index RENAME TO uix_user_role_iam_user_roles;

-- Rename foreign key constraints back
ALTER TABLE user_roles RENAME CONSTRAINT iam_user_roles_user_id_fkey TO user_roles_user_id_fkey;
ALTER TABLE user_roles RENAME CONSTRAINT iam_user_roles_role_id_fkey TO user_roles_role_id_fkey;
