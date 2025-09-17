from sqlalchemy.ext.asyncio import (
    AsyncEngine, async_sessionmaker, AsyncSession)


class PostgresSession:
    def __init__(self, async_engine: AsyncEngine):
        self.engine = async_engine

        self.AsyncSessionMaker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            info={"any_attribute": "any session available attribute data"}, )

    async def __aenter__(self):
        self.session = self.AsyncSessionMaker()
        print(f"Postgres SESSION CREATED successfully [OK]")
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:  # No session context manager error
            try:
                await self.session.commit()
                print(f"Postgres SESSION COMMIT success [OK]")
            except Exception as error:
                await self.session.rollback()
                print(f"Postgres SESSION ROLLBACK "
                      f"(due to SESSION COMMIT error) [ERROR]\n"
                      f"error: {error}")
                raise
        else:  # Session context manager error returned
            print(f"Postgres SESSION CONTEXT MANAGER [ERROR]:\n"
                  f"exc_type: {exc_type}\n"
                  f"exc_val: {exc_val}\n"
                  f"exc_tb: {exc_tb}\n")
            try:
                await self.session.rollback()
                print(f"Postgres SESSION ROLLBACK (due to session "
                      f"context manager inner error) [OK]\n")
            except Exception as error:
                print(f"Postgres SESSION ROLLBACK (due to session "
                      f"context manager inner error) [ERROR]:\n"
                      f"error: {error}")
                raise
        try:
            if self.session.is_active:
                await self.session.close()
                print(f"Postgres SESSION CLOSED successfully [OK]")
        except Exception as error:
            print(f"Postgres SESSION CLOSING error [ERROR]:\n"
                  f"error: {error}")
            raise
