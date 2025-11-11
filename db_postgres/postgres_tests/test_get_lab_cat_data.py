# ####################### DEBUG CODE (start) ###########################
# ######################################################################


if __name__ == "__main__":
    from db_postgres.postgres_conn_async.pgs_async_connection import PgsAsyncConnection
    from db_postgres.postgres_conn_async.postgres_async_session import PgsAsyncSession
    import asyncio
    from db_postgres.postgres_queries.qry_get_label_category_dict import get_label_category_dict_qry


    pgs_conn = PgsAsyncConnection()
    async with PgsAsyncSession(async_engine=pgs_conn.engine) as pgs_session:
        label_category_records = asyncio.run(
            main=get_label_category_dict_qry(
                ongoing_session=pgs_session,
                reversed_category_label_dict=False),
        debug=True)
        print(label_category_records)

        
# ########################## DEBUG CODE (end) ##########################
# ######################################################################
