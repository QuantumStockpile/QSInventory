from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "equipments" DROP COLUMN "balls";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "equipments" ADD "balls" JSONB;"""
