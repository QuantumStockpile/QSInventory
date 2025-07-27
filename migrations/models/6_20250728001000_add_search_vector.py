from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "equipments" ADD "search_vector" TEXT;
        CREATE INDEX "idx_equipments_name_serial" ON "equipments" ("name", "serial_number");
        CREATE INDEX "idx_equipments_search_vector" ON "equipments" ("search_vector");
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_equipments_search_vector";
        DROP INDEX "idx_equipments_name_serial";
        ALTER TABLE "equipments" DROP COLUMN "search_vector";
        """ 