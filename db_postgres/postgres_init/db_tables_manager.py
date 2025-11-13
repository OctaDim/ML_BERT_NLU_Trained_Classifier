from sqlalchemy import MetaData, text, Engine
from sqlalchemy.ext.asyncio import AsyncEngine


class DBTablesManagerSync:
    def __init__(self, pgs_sync_engine: Engine):
        self.engine = pgs_sync_engine

    def create_tables(self, metadata: MetaData) -> None:
        with self.engine.begin() as pgs_sync_conn:
            metadata.create_all(bind=pgs_sync_conn)
        print("\nDatabase tables initialized successfully [OK]")

    def drop_tables(self, metadata: MetaData) -> None:
        with self.engine.begin() as pgs_sync_conn:
            metadata.drop_all(bind=pgs_sync_conn)
        print("Database tables dropped successfully [OK]")

    def check_tables_exist(self, metadata: MetaData) -> bool:
        sql_query = ("SELECT EXISTS ("
                     "SELECT FROM information_schema.tables "
                     "WHERE table_name = :table_name)")

        with self.engine.connect() as pgs_sync_conn:
            for table_name in metadata.tables.keys():
                result = pgs_sync_conn.execute(
                    text(sql_query),
                    {"table_name": table_name})
                if not result.scalar():
                    return False
        return True


class DBTablesManagerAsync:
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
                if not result.scalar():
                    return False
        return True
