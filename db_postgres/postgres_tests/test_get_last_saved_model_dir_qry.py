# ####################### DEBUG CODE (start) ###########################
# ######################################################################

if __name__ == "__main__":
    async def test_get_last_saved_model_dir_qry():
        from db_postgres.postgres_conn.pgs_connection import PgsAsyncConnection
        from db_postgres.postgres_conn.postgres_session import PgsAsyncSession
        from db_postgres.postgres_queries.qry_get_last_saved_model_dir import get_last_saved_model_dir_qry
        # from ML_BERT_classifier.init_bert import init_and_start_bert_model
        # from db_postgres.postgres_init.db_tables_initialization import sync_initialize_db_tables
        # await sync_initialize_db_tables()
        # await init_and_start_bert_model()
        pgs_conn = PgsAsyncConnection()
        async with PgsAsyncSession(engine=pgs_conn.engine) as pgs_session:
            last_saved_model_dir_path = await get_last_saved_model_dir_qry(
                ongoing_session=pgs_session)
        print(f"last_saved_model_dir_path: {last_saved_model_dir_path}")
        return last_saved_model_dir_path


    import asyncio

    asyncio.run(main=test_get_last_saved_model_dir_qry(), debug=True)

# ########################## DEBUG CODE (end) ##########################
# ######################################################################
