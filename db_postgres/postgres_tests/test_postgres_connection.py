# ####################### DEBUG CODE (start) ###########################
# ######################################################################


async def test_connection():
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    from db_postgres.postgres_conn_async.postgres_async_session import PgsAsyncSession
    from db_postgres.postgres_conn_async.pgs_async_connection import (
        PgsAsyncConnection)
    pgs_conn = PgsAsyncConnection()
    async with PgsAsyncSession(engine=pgs_conn.engine) as pgs_session:
        print(f"pgs_conn: {pgs_session}")
    print(f"pgs_conn", {await pgs_conn.db_health_check()})
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main=test_connection(), debug=True)
# ########################## DEBUG CODE (end) ##########################
# ######################################################################
