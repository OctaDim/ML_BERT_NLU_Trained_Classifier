if __name__ == "__main__":
    from db_postgres.postgres_conn.pgs_connection import PgsSyncConnection
    from db_postgres.postgres_conn.postgres_session import PgsSyncSession

    pgs_sync_conn = PgsSyncConnection()
    with PgsSyncSession(engine=pgs_sync_conn.sync_engine) as pgs_sync_session:
        print(pgs_sync_session)
