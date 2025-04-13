WITH role_permissions AS (
            SELECT DISTINCT
                'p' AS ptype,
                r.scope || ':' || COALESCE(r.app_id::text, '') || ':' || r.role_name AS subject,
                res.scope || ':' || COALESCE(res.app_id::text, '') || ':' || res.resource_name AS object,
                perm.action AS action,
                COALESCE(rp.effect, 'allow') AS effect
            FROM iam_role_policies rp
            JOIN iam_roles r ON rp.role_id = r.id
            JOIN iam_permissions perm ON rp.permission_id = perm.id
            JOIN iam_resources res ON perm.resource_id = res.id
            WHERE r.scope = :policy_api_scope AND (:policy_api_appid IS NULL OR r.app_id = :policy_api_appid)
            AND res.scope = :policy_api_scope AND (:policy_api_appid IS NULL OR res.app_id = :policy_api_appid)
        ),
        user_permissions AS (
            SELECT DISTINCT
                'p' AS ptype,
                u.id::text AS subject,
                res.scope || ':' || COALESCE(res.app_id::text, '') || ':' || res.resource_name AS object,
                perm.action AS action,
                COALESCE(up.effect, 'allow') AS effect
            FROM iam_user_policies up
            JOIN users u ON up.user_id = u.id
            JOIN iam_permissions perm ON up.permission_id = perm.id
            JOIN iam_resources res ON perm.resource_id = res.id
            WHERE res.scope = :policy_api_scope AND (:policy_api_appid IS NULL OR res.app_id = :policy_api_appid)
        ),
        user_roles AS (
            SELECT DISTINCT
                'g' AS ptype,
                u.id::text AS subject,
                r.scope || ':' || COALESCE(r.app_id::text, '') || ':' || r.role_name AS object,
                NULL AS action,
                NULL AS effect
            FROM user_roles ur
            JOIN users u ON ur.user_id = u.id
            JOIN iam_roles r ON ur.role_id = r.id
            WHERE r.scope = :policy_api_scope AND (:policy_api_appid IS NULL OR r.app_id = :policy_api_appid)
        )
        SELECT ptype, subject, object, action, effect FROM role_permissions
        UNION ALL
        SELECT ptype, subject, object, action, effect FROM user_permissions
        UNION ALL
        SELECT ptype, subject, object, action, effect FROM user_roles