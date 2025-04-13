WITH user_roles AS (
    -- Get all roles assigned to the user
    SELECT
        r.id AS role_id,
        r.scope || ':' || COALESCE(r.app_id::text, '') || ':' || r.role_name AS role_name
    FROM user_roles ur
    JOIN iam_roles r ON ur.role_id = r.id
    JOIN users u ON ur.user_id = u.id
    WHERE u.id = :user_id
),
role_permissions AS (
    -- Get all role-based permissions for the user
    SELECT
        'p' AS ptype,                                           -- Casbin policy type: allow/deny
        ur.role_name AS subject,                                -- Role as the subject
        res.scope || ':' || COALESCE(res.app_id::text, '') || ':' || res.resource_name AS object,
        perm.action AS action,                                  -- Action
        COALESCE(rp.effect, 'allow') AS effect                  -- Allow/Deny
    FROM user_roles ur
    JOIN iam_role_policies rp ON ur.role_id = rp.role_id
    JOIN iam_permissions perm ON rp.permission_id = perm.id
    JOIN iam_resources res ON perm.resource_id = res.id
),
user_permissions AS (
    -- Get direct user-specific permissions
    SELECT
        'p' AS ptype,                                           -- Casbin policy type: allow/deny
        u.id::text AS subject,                                      -- User as Casbin subject
        res.scope || ':' || COALESCE(res.app_id::text, '') || ':' || res.resource_name AS object,
        perm.action AS action,                                  -- Action
        COALESCE(up.effect, 'allow') AS effect                  -- Allow/Deny
    FROM iam_user_policies up
    JOIN users u ON up.user_id = u.id
    JOIN iam_permissions perm ON up.permission_id = perm.id
    JOIN iam_resources res ON perm.resource_id = res.id
    WHERE u.id = :user_id
),
user_roles_mappings AS (
    -- Map user to roles for Casbin "g" rules
    SELECT
        'g' AS ptype,                                           -- Casbin group rule
        u.id::text AS subject,                                      -- User as Casbin subject
        ur.role_name AS object,                                 -- Role as Casbin object
        NULL AS action,                                         -- No action for "g" rules
        NULL AS effect                                          -- No effect for "g" rules
    FROM user_roles ur
    JOIN users u ON u.id = :user_id
)
-- Combine all policies into a single result set
SELECT ptype, subject, object, action, effect FROM role_permissions
UNION ALL
SELECT ptype, subject, object, action, effect FROM user_permissions
UNION ALL
SELECT ptype, subject, object, action, effect FROM user_roles_mappings;