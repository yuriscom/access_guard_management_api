WITH role_permissions AS (
    -- Get all permissions (allow/deny) for the specified role
    SELECT
        'p' as ptype,                                           -- Casbin policy type: allow or deny
        r.role_name AS subject,                                 -- Role as Casbin subject
        CONCAT(res.scope, '/', res.resource_name) AS object,    -- Scoped resource
        perm.action AS action,                                   -- Action
        CASE
            WHEN rp.effect = 'deny' THEN 'deny'
            ELSE 'allow'
        END AS effect
    FROM iam_roles r
    JOIN iam_role_policies rp ON rp.role_id = r.id
    JOIN iam_permissions perm ON rp.permission_id = perm.id
    JOIN iam_resources res ON perm.resource_id = res.id
    WHERE r.id = :role_id
    AND NOT coalesce(r.synthetic, false)
)
SELECT * FROM role_permissions;