if __name__ == "__main__":
    import asyncio
    from db_postgres.postgres_async_conn.pgs_async_connection import (
        PostgresConnection)
    from db_postgres.postgres_async_conn.postgres_async_session import (
        PostgresSession)
    from db_postgres.postgres_queries.qry_get_direct_category_by_text import (
        get_direct_category_by_text)


    async def test_obtain_direct_category_by_text():
        pgs_conn = PostgresConnection()
        async with PostgresSession(async_engine=pgs_conn.engine) as pgs_session:
            direct_category = await get_direct_category_by_text(
                ongoing_session=pgs_session,
                account_id="30",
                account_username="globalhome",
                direct_text="врач по глазам")
            print(f"direct_category: {direct_category}")


    asyncio.run(main=test_obtain_direct_category_by_text(),
                debug=True)
