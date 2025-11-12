from typing import Union

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import text

from configs.settings import (
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT,
    POSTGRES_DB_NAME, ALCHEMY_OPTIONS)
from meta_classes.singlton_meta import SingletonMeta

Base = declarative_base()


class PgsSyncConnection(metaclass=SingletonMeta):
    def __init__(
            self,
            user: str = None,
            password: Union[str, None] = None,
            host: str = None,
            port: int = None,
            db_name: str = None,
            async_driver_prefix: str = "postgresql+psycopg2",
            **kwargs
    ) -> None:
        db_user = POSTGRES_USER if user is None else user
        db_password = POSTGRES_PASSWORD if password is None else password
        db_host = POSTGRES_HOST if host is None else host
        db_port = POSTGRES_PORT if port is None else port
        db_name = POSTGRES_DB_NAME if db_name is None else db_name

        self.orm_engine_url = (f"{async_driver_prefix}://"
                               f"{db_user}:{db_password}@"
                               f"{db_host}:{db_port}/{db_name}")
        self.engine = self.create_sync_engine()

    def create_sync_engine(self) -> Engine:
        try:
            sync_engine = create_engine(
                url=self.orm_engine_url,
                echo=ALCHEMY_OPTIONS.ALCHEMY_ORM_RAW_SQL_LOGS,
                future=ALCHEMY_OPTIONS.ALCHEMY_USE_FUTURE_ALCHEMY,
                pool_pre_ping=ALCHEMY_OPTIONS.ALCHEMY_POOL_PRE_PING,
                pool_size=ALCHEMY_OPTIONS.ALCHEMY_CONST_CONN_POOL_SIZE,
                max_overflow=ALCHEMY_OPTIONS.ALCHEMY_TEMP_CONN_MAX_OVERFLOW,
                pool_recycle=ALCHEMY_OPTIONS.ALCHEMY_POOL_RECYCLE,
                pool_timeout=ALCHEMY_OPTIONS.ALCHEMY_POOL_TIMEOUT, )
            print("Postgres DB SYNC ENGINE CREATED [OK]")
            return sync_engine
        except Exception as error:
            print(f"Postgres DB SYNC ENGINE CREATING [ERROR]: "
                  f"error: {error}")
            raise

    def db_health_check(self) -> bool:
        """Check database connection availability (health status)"""
        try:
            with self.engine.connect() as sync_engine_conn:
                sync_engine_conn.execute(text("SELECT 1"))
            return True
        except Exception as error:
            error_log = (f"Postgres DB HEALTH check [ERROR]: "
                         f"error: {error}")
            print(error_log)
            return False

    def dispose_connection(self) -> None:
        """Close all database connections"""
        try:
            self.engine.dispose()
            print(f"Postgres DB SYNC CONNECTIONS CLOSED successfully [OK]")
        except Exception as error:
            print(f"Postgres DB SYNC CONNECTIONS CLOSING [ERROR]: "
                  f"error: {error}")


def close_all_db_connections():
    pgs_conn = PgsSyncConnection()
    pgs_conn.dispose_connection()
