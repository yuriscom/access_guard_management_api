CREATE TABLE IF NOT EXISTS policy_refresh_hooks (
    id SERIAL PRIMARY KEY,
    scope VARCHAR NOT NULL CHECK (scope IN ('SMC', 'PRODUCT', 'APP')),
    app_id UUID NOT NULL,
    url TEXT NOT NULL,
    secret TEXT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_hooks_scope_app_id ON policy_refresh_hooks (scope, app_id);