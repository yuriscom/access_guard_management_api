WITH role_permissions AS (
    -- Role-based policies
    SELECT DISTINCT
        'p' AS ptype,                                           -- Role-permission policy
        r.scope || ':' || COALESCE(r.app_id::text, '') || ':' || r.role_name AS subject,
        res.scope || ':' || COALESCE(res.app_id::text, '') || ':' || res.resource_name AS object,
        perm.action AS action,                                  -- Action (read, write, etc.)
        COALESCE(rp.effect, 'allow') AS effect                  -- Allow/Deny
    FROM iam_role_policies rp
    JOIN iam_roles r ON rp.role_id = r.id
    JOIN iam_permissions perm ON rp.permission_id = perm.id
    JOIN iam_resources res ON perm.resource_id = res.id
),
user_permissions AS (
    -- User-specific policies
    SELECT DISTINCT
        'p' AS ptype,                                           -- User-permission policy
        u.id::text AS subject,                                      -- User directly as subject
        res.scope || ':' || COALESCE(res.app_id::text, '') || ':' || res.resource_name AS object,
        perm.action AS action,                                  -- Action (read, write, etc.)
        COALESCE(up.effect, 'allow') AS effect                  -- Allow/Deny
    FROM iam_user_policies up
    JOIN users u ON up.user_id = u.id
    JOIN iam_permissions perm ON up.permission_id = perm.id
    JOIN iam_resources res ON perm.resource_id = res.id
),
user_roles AS (
    -- User-to-role mappings
    SELECT DISTINCT
        'g' AS ptype,                                           -- User-role mapping
        u.id::text AS subject,                                      -- User as subject
        r.scope || ':' || COALESCE(r.app_id::text, '') || ':' || r.role_name AS object,
        NULL AS action,                                         -- No action for "g" rules
        NULL AS effect                                          -- No effect for "g" rules
    FROM user_roles ur
    JOIN users u ON ur.user_id = u.id
    JOIN iam_roles r ON ur.role_id = r.id
)
-- Combine all policies: role, user, and group mappings
SELECT ptype, subject, object, action, effect FROM role_permissions
UNION ALL
SELECT ptype, subject, object, action, effect FROM user_permissions
UNION ALL
SELECT ptype, subject, object, action, effect FROM user_roles