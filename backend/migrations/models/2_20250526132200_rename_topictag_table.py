from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "topictag" RENAME TO "topic_tag";
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "topic_tag" RENAME TO "topictag";
    """
