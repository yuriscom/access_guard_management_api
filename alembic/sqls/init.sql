-- public.iam_resources definition

-- Drop table

-- DROP TABLE public.iam_resources;

CREATE TABLE public.iam_resources (
	id serial NOT NULL,
	"scope" scope NOT NULL,
	app_id int4 NULL,
	resource_name varchar(255) NOT NULL,
	description text NULL,
	created_at timestamp NULL DEFAULT now(),
	synthetic bool NULL DEFAULT false,
	synthetic_pattern varchar(255) NULL,
	CONSTRAINT iam_resources_pkey PRIMARY KEY (id),
	CONSTRAINT iam_resources_app_id_fkey FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX uix_scope_app_resource ON public.iam_resources USING btree (scope, COALESCE(app_id, '-1'::integer), resource_name);


-- public.iam_roles definition

-- Drop table

-- DROP TABLE public.iam_roles;

CREATE TABLE public.iam_roles (
	id serial NOT NULL,
	"scope" scope NOT NULL,
	app_id int4 NULL,
	role_name varchar(255) NOT NULL,
	description text NULL,
	created_at timestamp NULL DEFAULT now(),
	synthetic bool NULL DEFAULT false,
	synthetic_pattern varchar(255) NULL,
	CONSTRAINT iam_roles_pkey PRIMARY KEY (id),
	CONSTRAINT iam_roles_app_id_fkey FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX uix_scope_app_role ON public.iam_roles USING btree (scope, COALESCE(app_id, '-1'::integer), role_name);

-- public.iam_permissions definition

-- Drop table

-- DROP TABLE public.iam_permissions;

CREATE TABLE public.iam_permissions (
	id serial NOT NULL,
	resource_id int4 NOT NULL,
	"action" varchar(50) NOT NULL,
	created_at timestamp NULL DEFAULT now(),
	CONSTRAINT iam_permissions_pkey PRIMARY KEY (id),
	CONSTRAINT uix_resource_action UNIQUE (resource_id, action),
	CONSTRAINT iam_permissions_resource_id_fkey FOREIGN KEY (resource_id) REFERENCES iam_resources(id) ON DELETE CASCADE
);


-- public.iam_role_policies definition

-- Drop table

-- DROP TABLE public.iam_role_policies;

CREATE TABLE public.iam_role_policies (
	id int4 NOT NULL DEFAULT nextval('iam_policies_id_seq'::regclass),
	role_id int4 NOT NULL,
	permission_id int4 NOT NULL,
	created_at timestamp NULL DEFAULT now(),
	effect varchar NOT NULL DEFAULT 'allow'::character varying,
	CONSTRAINT iam_policies_effect_check CHECK (((effect)::text = ANY ((ARRAY['allow'::character varying, 'deny'::character varying])::text[]))),
	CONSTRAINT iam_policies_pkey PRIMARY KEY (id),
	CONSTRAINT iam_policies_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES iam_permissions(id) ON DELETE CASCADE,
	CONSTRAINT iam_policies_role_id_fkey FOREIGN KEY (role_id) REFERENCES iam_roles(id) ON DELETE CASCADE
);


-- public.iam_user_policies definition

-- Drop table

-- DROP TABLE public.iam_user_policies;

CREATE TABLE public.iam_user_policies (
	id serial NOT NULL,
	user_id int4 NOT NULL,
	permission_id int4 NOT NULL,
	created_at timestamp NULL DEFAULT now(),
	effect varchar NOT NULL DEFAULT 'allow'::character varying,
	CONSTRAINT iam_user_policies_effect_check CHECK (((effect)::text = ANY (ARRAY[('allow'::character varying)::text, ('deny'::character varying)::text]))),
	CONSTRAINT iam_user_policies_pkey PRIMARY KEY (id),
	CONSTRAINT iam_policies_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	CONSTRAINT iam_user_policies_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES iam_permissions(id) ON DELETE CASCADE
);


-- public.user_roles definition

-- Drop table

-- DROP TABLE public.user_roles;

CREATE TABLE public.user_roles (
	id serial NOT NULL,
	user_id int4 NOT NULL,
	role_id int4 NOT NULL,
	created_at timestamp NULL DEFAULT now(),
	CONSTRAINT user_roles_pkey PRIMARY KEY (id),
	CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES iam_roles(id) ON DELETE CASCADE,
	CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);