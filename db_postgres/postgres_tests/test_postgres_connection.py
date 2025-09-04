# ####################### DEBUG CODE (start) ###########################
# ######################################################################
async def test_connection():
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    from db_postgres.postgres_async_conn.pgs_async_connection import (
        PostgresConnection)
    pgs_connection = PostgresConnection()
    async with pgs_connection.async_session() as pgs_session:
        print(f"pgs_conn: {pgs_session}")
    print(f"pgs_conn", {await pgs_connection.db_health_check()})
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main=test_connection(), debug=True)
# ########################## DEBUG CODE (end) ##########################
# ######################################################################
