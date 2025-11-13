if __name__ == "__main__":
    import asyncio
    from db_postgres.postgres_conn.pgs_connection import (
        PgsAsyncConnection)
    from db_postgres.postgres_conn.postgres_session import (
        PgsAsyncSession)
    from db_postgres.postgres_queries.qry_get_direct_category_by_text import (
        get_direct_category_by_text)


    async def test_obtain_direct_category_by_text():
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine) as pgs_session:
            direct_category = await get_direct_category_by_text(
                ongoing_session=pgs_session,
                account_id="30",
                account_username="globalhome",
                direct_text="врач по глазам")
            print(f"direct_category: {direct_category}")


    asyncio.run(main=test_obtain_direct_category_by_text(),
                debug=True)
