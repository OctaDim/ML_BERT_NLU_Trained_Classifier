# ####################### DEBUG CODE (start) ###########################
# ######################################################################


if __name__ == "__main__":
    import asyncio
    from db_postgres.postgres_conn_async.pgs_async_connection import (
        PgsAsyncConnection)
    from db_postgres.postgres_conn_async.postgres_async_session import (
        PgsAsyncSession)
    from db_postgres.postgres_queries.qry_get_lab_idx_and_id_dict import (
        get_label_idx_and_id_dict_qry)


async def test_get_label_index_id_dict_qry():
    pgs_conn = PgsAsyncConnection()
    async with PgsAsyncSession(engine=pgs_conn.engine,
                               log_good_ops=True) as pgs_session:
        pgs_lab_index_and_id_dict = await get_label_idx_and_id_dict_qry(
            ongoing_session=pgs_session)
        print(pgs_lab_index_and_id_dict)


asyncio.run(main=test_get_label_index_id_dict_qry(),
            debug=True)

# ########################## DEBUG CODE (end) ##########################
# ######################################################################
