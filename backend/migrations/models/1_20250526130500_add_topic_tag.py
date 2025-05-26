from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "topictag" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "tag_id" UUID NOT NULL REFERENCES "tag" ("id") ON DELETE CASCADE,
    "topic_id" UUID NOT NULL REFERENCES "topic" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_topictag_topic_i_tag_id_b4b4ca" UNIQUE ("topic_id", "tag_id")
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "topictag";"""
