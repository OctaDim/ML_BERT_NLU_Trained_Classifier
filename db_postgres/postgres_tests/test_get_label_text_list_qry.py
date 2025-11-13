if __name__ == "__main__":
    from db_postgres.postgres_conn.pgs_connection import (
        PgsAsyncConnection)
    from db_postgres.postgres_conn.postgres_session import (
        PgsAsyncSession)
    import asyncio
    from db_postgres.postgres_queries.qry_get_direct_category_text_dicts_list import get_direct_cat_text_dicts_list_qry


    async def test_get_label_text_list_qry():
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine) as pgs_session:
            pgs_text_lab_list = await get_direct_cat_text_dicts_list_qry(
                ongoing_session=pgs_session)
            for cur_row in pgs_text_lab_list:
                print(cur_row)


    asyncio.run(main=test_get_label_text_list_qry(), debug=True)
