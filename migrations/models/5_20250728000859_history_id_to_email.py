from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "history" ADD "email" VARCHAR(256) NOT NULL;
        ALTER TABLE "history" DROP COLUMN "user_id";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "history" ADD "user_id" INT NOT NULL;
        ALTER TABLE "history" DROP COLUMN "email";"""
