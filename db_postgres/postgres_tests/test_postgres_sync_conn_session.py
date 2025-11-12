if __name__ == "__main__":
    from db_postgres.postgres_conn_sync.pgs_sync_connection import (
        PgsSyncConnection)
    from db_postgres.postgres_conn_sync.postgres_sync_session import (
        PgsSyncSession)

    pgs_sync_conn = PgsSyncConnection()
    with PgsSyncSession(engine=pgs_sync_conn.sync_engine) as pgs_sync_session:
        print(pgs_sync_session)
