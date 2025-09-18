from typing import Union

from sqlalchemy.ext.asyncio import (
    create_async_engine)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import text

from configs.settings import (
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT,
    POSTGRES_DB_NAME, ALCHEMY_OPTIONS)
from meta_classes.singlton_meta import SingletonMeta

Base = declarative_base()


class PostgresConnection(metaclass=SingletonMeta):
    def __init__(self,
                 user: str = None,
                 password: Union[str, None] = None,
                 host: str = None,
                 port: int = None,
                 db_name: str = None,
                 **kwargs) -> None:
        self.db_user = POSTGRES_USER if user is None else user
        self.db_password = POSTGRES_PASSWORD if password is None else password
        self.db_host = POSTGRES_HOST if host is None else host
        self.db_port = POSTGRES_PORT if port is None else port
        self.db_name = POSTGRES_DB_NAME if db_name is None else db_name

        async_driver_prefix = "postgresql+asyncpg"
        self.orm_engine_url = (
            f"{async_driver_prefix}://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}")

        self.engine = self.create_async_engine()

    def create_async_engine(self):
        try:
            engine = create_async_engine(
                url=self.orm_engine_url,
                echo=ALCHEMY_OPTIONS.ALCHEMY_ORM_RAW_SQL_CONSOLE_LOGS,
                future=ALCHEMY_OPTIONS.ALCHEMY_USE_FUTURE_ALCHEMY,
                pool_pre_ping=ALCHEMY_OPTIONS.ALCHEMY_POOL_PRE_PING,
                pool_size=ALCHEMY_OPTIONS.ALCHEMY_CONST_CONN_POOL_SIZE,
                max_overflow=ALCHEMY_OPTIONS.ALCHEMY_TEMP_CONN_MAX_OVERFLOW,
                pool_recycle=ALCHEMY_OPTIONS.ALCHEMY_POOL_RECYCLE,
                pool_timeout=ALCHEMY_OPTIONS.ALCHEMY_POOL_TIMEOUT, )
            print("Postgres DB ENGINE CREATED [OK]")
            return engine
        except Exception as error:
            print(f"Postgres DB ENGINE CREATING [ERROR]: "
                  f"error: {error}")
            raise

    async def db_health_check(self) -> bool:
        """Check database connection availability (health status)"""
        try:
            async with self.engine.connect() as engine_conn:
                await engine_conn.execute(text("SELECT 1"))
            return True
        except Exception as error:
            error_log = (f"Postgres DB HEALTH check [ERROR]: "
                         f"error: {error}")
            print(error_log)
            return False

    async def dispose(self) -> None:
        """Close all database connections"""
        try:
            await self.engine.dispose()
            print(f"Postgres DB CONNECTIONS CLOSED successfully [OK]")
        except Exception as error:
            print(f"Postgres DB CONNECTIONS CLOSING [ERROR]: "
                  f"error: {error}")
