if __name__ == "__main__":
    import asyncio
    from db_postgres.postgres_async_conn.pgs_async_connection import (
        PostgresConnection)
    from db_postgres.postgres_async_conn.postgres_async_session import (
        PostgresSession)
    from db_postgres.postgres_queries.qry_get_direct_category_text_by_acc_dict import (
        get_direct_categ_text_by_acc_dict_qry)


async def test_get_direct_category_text_by_acc_dict_qry():
    account_id = "30"
    account_username = "globalhome"

    pgs_conn = PostgresConnection()
    async with PostgresSession(async_engine=pgs_conn.engine) as pgs_session:
        pgs_direct_cat_dict = await get_direct_categ_text_by_acc_dict_qry(
            ongoing_session=pgs_session,
            account_id=account_id,
            account_username=account_username,
            reversed_direct_text_cat_dict=True
        )

    print(pgs_direct_cat_dict)


asyncio.run(
    main=test_get_direct_category_text_by_acc_dict_qry(),
    debug=True)
