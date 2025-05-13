-- iam_role: turn synthetic_data to JSONB
ALTER TABLE iam_roles RENAME COLUMN synthetic_pattern TO synthetic_data;
ALTER TABLE iam_roles ALTER COLUMN synthetic_data TYPE JSONB USING
    jsonb_build_object('resource', synthetic_data, 'actions', ARRAY['*']);
update iam_roles set synthetic_data = null where coalesce(synthetic, false) is false;

-- iam_resource: turn synthetic_data to JSONB
ALTER TABLE iam_resources RENAME COLUMN synthetic_pattern TO synthetic_data;
ALTER TABLE iam_resources ALTER COLUMN synthetic_data TYPE JSONB using synthetic_data::jsonb;


DO $$
DECLARE
    am_app_id UUID;
BEGIN
    -- 1. Get AM id
    SELECT id INTO am_app_id FROM apps WHERE name = 'Access Manager';

    -- 2. Delete old roles
    delete from iam_roles where role_name = 'OrgAdmin' and app_id=am_app_id and org_id is NULL;
    delete from iam_roles where role_name = 'PolicyReader' and scope='SMC' and app_id=am_app_id;
    delete from iam_roles where role_name = 'BillingViewer' and scope='SMC' and app_id=am_app_id;
    delete from iam_roles where role_name = 'ReportingUser' and scope='SMC' and app_id=am_app_id;

    -- 3. Insert new built-in roles
    INSERT INTO iam_roles (scope, app_id, role_name, description, created_at, synthetic, synthetic_data)
    VALUES ('SMC', am_app_id, 'SMC_IAM_Viewer', 'VIEW IAM resources for a specific product', now(), true,
        '{"actions": ["read"], "resource": "iam"}')
    ON CONFLICT DO NOTHING;

    -- 4. Update role names per naming convention
    update iam_roles set role_name = 'SMC_IAM_Manager' where role_name='IAMManager';
    update iam_roles set role_name = 'SMC_IAM_Policy_Reader' where role_name='PolicyReader';
END $$;


