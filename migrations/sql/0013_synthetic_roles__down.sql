DO $$
DECLARE
    am_app_id UUID;
BEGIN
    SELECT id INTO am_app_id FROM apps WHERE name = 'Access Manager';

    delete from iam_roles where role_name = 'SMC_IAM_Viewer' and app_id=am_app_id;

    update iam_roles set role_name = 'IAMManager' where role_name='SMC_IAM_Manager';
    update iam_roles set role_name = 'PolicyReader' where role_name='SMC_IAM_Policy_Reader';
END $$;