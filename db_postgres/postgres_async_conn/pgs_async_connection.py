from contextlib import asynccontextmanager
from typing import Union, AsyncIterator

from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession, async_sessionmaker)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import text

from configs.settings import (
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT,
    POSTGRES_DB_NAME, ALCHEMY_OPTIONS)

Base = declarative_base()


class PostgresConnection:
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

        self.engine = create_async_engine(
            url=self.orm_engine_url,
            echo=ALCHEMY_OPTIONS.ALCHEMY_ORM_RAW_SQL_CONSOLE_LOGS,
            future=ALCHEMY_OPTIONS.ALCHEMY_USE_FUTURE_ALCHEMY,
            pool_pre_ping=ALCHEMY_OPTIONS.ALCHEMY_POOL_PRE_PING,
            pool_size=ALCHEMY_OPTIONS.ALCHEMY_CONST_CONN_POOL_SIZE,
            max_overflow=ALCHEMY_OPTIONS.ALCHEMY_TEMP_CONN_MAX_OVERFLOW,
            pool_recycle=ALCHEMY_OPTIONS.ALCHEMY_POOL_RECYCLE,
            pool_timeout=ALCHEMY_OPTIONS.ALCHEMY_POOL_TIMEOUT, )

        self.AsyncSessionMaker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            info={"any_attribute": "any session available attribute data"}, )

    @asynccontextmanager
    async def async_session(self) -> AsyncIterator[AsyncSession]:
        """Hardly controlled Session via decorator, yield and try-except.
        Let's carefully control execution before and after the session"""
        async with self.AsyncSessionMaker() as session:
            try:
                print(f"\nPostgres SESSION CREATED [OK]")
                yield session
                await session.commit()
                print("Postgres SESSION COMMIT successfully [OK]")
            except Exception as error:
                await session.rollback()
                print(f"Postgres SESSION ROLLBACK dut to error [ERROR]:\n"
                      f"error: {error}\n"
                      f"self.db_user: {self.db_user}\n"
                      f"self.db_password: ***\n"
                      f"self.db_host: {self.db_host}\n"
                      f"self.db_port: {self.db_port}\n"
                      f"self.db_name: {self.db_name}\n")
                raise
            finally:
                await session.close()
                print("Postgres SESSION CLOSED successfully [OK]")

    async def db_health_check(self) -> bool:
        """Check database connection availability (health status)"""
        try:
            async with self.engine.connect() as engine_conn:
                await engine_conn.execute(text("SELECT 1"))
            return True
        except Exception as error:
            print(f"Postgres Database HEALTH check [ERROR]: error: {error}")
            return False

    async def dispose(self) -> None:
        """Close all database connections"""
        await self.engine.dispose()
        print(f"Postgres CONNECTION CLOSED successfully [OK]")

# # ####################### DEBUG CODE (start) #########################
# # ####################################################################
# async def test_connection():
#     print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
#     pgs_connection = PostgresConnection()
#     async with pgs_connection.async_session() as pgs_session:
#         print(f"pgs_conn: {pgs_session}")
#     print(f"pgs_conn", {await pgs_connection.db_health_check()})
#     print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
# import asyncio
# asyncio.run(main=test_connection(), debug=True)
# # ######################## DEBUG CODE (end) ##########################
# # ####################################################################
