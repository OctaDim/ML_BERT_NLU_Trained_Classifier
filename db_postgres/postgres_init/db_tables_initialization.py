from db_postgres.postgres_conn.pgs_connection import (
    PgsAsyncConnection, PgsSyncConnection)
from db_postgres.postgres_init.db_tables_manager import (
    DBTablesManagerSync, DBTablesManagerAsync)
from db_postgres.postgres_init.declarative_base_model import Base


def sync_initialize_db_tables():
    from db_postgres.postgres_init import db_tables_init_imports as imports
    model_imports = imports  # DO NOT REMOVE!!!: for staying import above when auto linter
    sync_pgs_conn = PgsSyncConnection()
    if sync_pgs_conn.db_health_check():
        tables_manager = DBTablesManagerSync(pgs_sync_engine=sync_pgs_conn.engine)
        tables_manager.create_tables(metadata=Base.metadata)
    else:
        print("DB POSTGRES HEALTH CHECK [ERROR]: \n")


async def async_initialize_db_tables():
    from db_postgres.postgres_init import db_tables_init_imports as imports
    model_imports = imports  # DO NOT REMOVE!!!: for staying import above when auto linter
    pgs_conn = PgsAsyncConnection()
    if await pgs_conn.db_health_check():
        tables_manager = DBTablesManagerAsync(pgs_async_engine=pgs_conn.engine)
        await tables_manager.create_tables(metadata=Base.metadata)
    else:
        print("DB POSTGRES HEALTH CHECK [ERROR]: \n")


if __name__ == "__main__":
    def test_initialize_db_tables(initialize_sync: bool = True):
        if initialize_sync:
            sync_initialize_db_tables()  # Sync option
        else:
            import asyncio
            asyncio.run(main=async_initialize_db_tables(), debug=True)  # Async option


    # test_initialize_db_tables(initialize_sync=False)
    test_initialize_db_tables(initialize_sync=True)
