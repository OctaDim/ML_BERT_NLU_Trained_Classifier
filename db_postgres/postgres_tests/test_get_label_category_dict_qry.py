if __name__ == "__main__":
    import asyncio
    from db_postgres.postgres_async_conn.pgs_async_connection import (
        PostgresConnection)
    from db_postgres.postgres_queries.qry_get_label_category_dict import (
        get_label_category_dict_qry)

    pgs_conn = PostgresConnection()
    asyncio.run(
        main=get_label_category_dict_qry(ongoing_session=pgs_conn.engine,
                                         reversed_category_label_dict=False),
        debug=True)
