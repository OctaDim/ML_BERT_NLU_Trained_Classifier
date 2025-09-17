from db_postgres.postgres_async_conn.db_tables_manager import (
    DBTablesManager)
from db_postgres.postgres_async_conn.pgs_async_connection import (
    PostgresConnection, Base)


async def initialize_db_tables():
    from db_postgres.postgres_init import db_tables_init_imports as imports
    model_imports = imports  # DO NOT REMOVE!!!: for staying import above when auto linter
    pgs_conn = PostgresConnection()
    if await pgs_conn.db_health_check():
        tables_manager = DBTablesManager(pgs_async_engine=pgs_conn.engine)
        await tables_manager.create_tables(metadata=Base.metadata)
    else:
        print("DB POSTGRES HEALTH CHECK [ERROR]: \n")


# Manual DB tables initialization
if __name__ == "__main__":
    import asyncio

    asyncio.run(main=initialize_db_tables(), debug=True)
