# ####################### DEBUG CODE (start) ###########################
# ######################################################################


if __name__ == "__main__":
    from db_postgres.postgres_conn_async.pgs_async_connection import (
        PgsAsyncConnection)
    from db_postgres.postgres_conn_async.postgres_async_session import (
        PgsAsyncSession)
    from db_postgres.postgres_queries.qry_get_label_text_dict import (
        get_label_text_dict_qry)
    import asyncio


    async def test_get_text_label_dict_qry():
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine) as pgs_session:
            pgs_text_lab_dict = await get_label_text_dict_qry(
                ongoing_session=pgs_session,
                reversed_text_label_dict=True)
            print(f"pgs_text_lab_dict: {pgs_text_lab_dict}")


    asyncio.run(main=test_get_text_label_dict_qry(), debug=True)

# ########################## DEBUG CODE (end) ##########################
# ######################################################################
