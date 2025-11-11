if __name__ == "__main__":
    import asyncio
    from db_postgres.postgres_conn_async.pgs_async_connection import (
        PgsAsyncConnection)
    from db_postgres.postgres_conn_async.postgres_async_session import (
        PgsAsyncSession)
    from db_postgres.postgres_queries.qry_get_direct_categ_text_by_acc_dict import (
        get_direct_cat_text_by_acc_dict_qry)


async def test_get_direct_category_text_by_acc_dict_qry():
    account_id = "30"
    account_username = "globalhome"

    pgs_conn = PgsAsyncConnection()
    async with PgsAsyncSession(async_engine=pgs_conn.engine) as pgs_session:
        pgs_direct_cat_dict = await get_direct_cat_text_by_acc_dict_qry(
            ongoing_session=pgs_session,
            account_id=account_id,
            account_username=account_username,
            reversed_direct_text_cat_dict=True
        )

    print(pgs_direct_cat_dict)


asyncio.run(
    main=test_get_direct_category_text_by_acc_dict_qry(),
    debug=True)
