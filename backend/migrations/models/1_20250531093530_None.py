from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "tag" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "slug" VARCHAR(50) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "user" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
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
CREATE TABLE IF NOT EXISTS "topic" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "author_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "pendingpost" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "content" TEXT NOT NULL,
    "parent_post_id" UUID,
    "author_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "topic_id" UUID NOT NULL REFERENCES "topic" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aianalysis" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "decision" VARCHAR(20) NOT NULL,
    "confidence_score" DOUBLE PRECISION NOT NULL,
    "analysis_text" TEXT NOT NULL,
    "feedback_text" TEXT NOT NULL,
    "processing_time_ms" INT NOT NULL,
    "pending_post_id" UUID NOT NULL REFERENCES "pendingpost" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "post" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "content" TEXT NOT NULL,
    "author_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "parent_post_id" UUID REFERENCES "post" ("id") ON DELETE CASCADE,
    "topic_id" UUID NOT NULL REFERENCES "topic" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "topic_tag" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "tag_id" UUID NOT NULL REFERENCES "tag" ("id") ON DELETE CASCADE,
    "topic_id" UUID NOT NULL REFERENCES "topic" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_topic_tag_topic_i_d9d5c7" UNIQUE ("topic_id", "tag_id")
);
CREATE TABLE IF NOT EXISTS "userevent" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "event_type" VARCHAR(50) NOT NULL,
    "ip_address" VARCHAR(45),
    "user_agent" VARCHAR(255),
    "resource_type" VARCHAR(50),
    "resource_id" UUID,
    "metadata" JSONB,
    "user_id" UUID REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "usersession" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "ip_address" VARCHAR(45) NOT NULL,
    "user_agent" VARCHAR(255) NOT NULL,
    "session_token" VARCHAR(255) NOT NULL,
    "expires_at" TIMESTAMPTZ NOT NULL,
    "is_active" BOOL NOT NULL DEFAULT True,
    "user_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
