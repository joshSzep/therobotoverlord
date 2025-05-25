from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "user" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password_hash" VARCHAR(255) NOT NULL,
    "display_name" VARCHAR(100) NOT NULL,
    "is_verified" BOOL NOT NULL DEFAULT False,
    "verification_token" VARCHAR(255),
    "last_login" TIMESTAMPTZ,
    "failed_login_attempts" INT NOT NULL DEFAULT 0,
    "role" VARCHAR(9) NOT NULL DEFAULT 'user',
    "is_locked" BOOL NOT NULL DEFAULT False
);
COMMENT ON COLUMN "user"."role" IS 'USER: user\nMODERATOR: moderator\nADMIN: admin';
COMMENT ON TABLE "user" IS 'User model with authentication fields.';
CREATE TABLE IF NOT EXISTS "loginattempt" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "ip_address" VARCHAR(45) NOT NULL,
    "user_agent" VARCHAR(255) NOT NULL,
    "success" BOOL NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" UUID REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "loginattempt" IS 'Login attempt model for security monitoring.';
CREATE TABLE IF NOT EXISTS "userevent" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "event_type" VARCHAR(50) NOT NULL,
    "ip_address" VARCHAR(45),
    "user_agent" VARCHAR(255),
    "resource_type" VARCHAR(50),
    "resource_id" UUID,
    "metadata" JSONB,
    "user_id" UUID REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "userevent" IS 'Model for tracking user events and activities.';
CREATE TABLE IF NOT EXISTS "usersession" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deleted_at" TIMESTAMPTZ,
    "ip_address" VARCHAR(45) NOT NULL,
    "user_agent" VARCHAR(255) NOT NULL,
    "session_token" VARCHAR(255) NOT NULL,
    "expires_at" TIMESTAMPTZ NOT NULL,
    "is_active" BOOL NOT NULL DEFAULT True,
    "user_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "usersession" IS 'User session model for tracking active sessions.';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
