 -- Rename the table
ALTER TABLE policy_refresh_hooks RENAME TO iam_policy_refresh_hooks;

-- Rename the primary key constraint
ALTER INDEX policy_refresh_hooks_pkey RENAME TO iam_policy_refresh_hooks_pkey;

-- Rename the check constraint
ALTER TABLE iam_policy_refresh_hooks RENAME CONSTRAINT policy_refresh_hooks_scope_check TO iam_policy_refresh_hooks_scope_check;

-- Rename the index on (scope, app_id)
ALTER INDEX ix_hooks_scope_app_id RENAME TO ix_iam_hooks_scope_app_id;