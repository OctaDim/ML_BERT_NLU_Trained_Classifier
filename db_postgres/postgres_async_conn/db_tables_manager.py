from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import AsyncEngine


class DBTablesManager:
    def __init__(self, pgs_async_engine: AsyncEngine):
        self.engine = pgs_async_engine

    async def create_tables(self, metadata: MetaData) -> None:
        async with self.engine.begin() as pgs_conn:
            await pgs_conn.run_sync(metadata.create_all)
        print("\nDatabase tables initialized successfully [OK]")

    async def drop_tables(self, metadata: MetaData) -> None:
        async with self.engine.begin() as pgs_conn:
            await pgs_conn.run_sync(metadata.drop_all)
        print("Database tables dropped successfully [OK]")

    async def check_tables_exist(self, metadata: MetaData) -> bool:
        sql_query = ("SELECT EXISTS ("
                     "SELECT FROM information_schema.tables "
                     "WHERE table_name = :table_name)")

        async with self.engine.connect() as pgs_conn:
            for table_name in metadata.tables.keys():
                result = await pgs_conn.execute(
                    text(sql_query),
                    {"table_name": table_name})
                exists = result.scalar()
                if not exists:
                    return False
        return True
