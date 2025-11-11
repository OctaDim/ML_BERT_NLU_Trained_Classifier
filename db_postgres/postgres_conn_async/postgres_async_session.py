from sqlalchemy.ext.asyncio import (
    AsyncEngine, async_sessionmaker, AsyncSession)


class PgsAsyncSession:
    def __init__(self, async_engine: AsyncEngine,
                 log_good_ops: bool = False):
        self.engine = async_engine
        self.AsyncSessionMaker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            info={"any_attribute": "any session available attribute data"}, )

        self.logging_ok_ops = log_good_ops

    async def __aenter__(self) -> AsyncSession:
        try:
            self.session = self.AsyncSessionMaker()
            ok_log = f"Postgres SESSION CREATED successfully [OK]"
            print(ok_log) if self.logging_ok_ops else None
            return self.session
        except Exception as error:
            print(f"Postgres SESSION CREATING [ERROR]")
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if not exc_type:  # No session context manager error
            try:
                await self.session.commit()
                ok_log = f"Postgres SESSION COMMIT success [OK]"
                print(ok_log) if self.logging_ok_ops else None
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
                ok_log = f"Postgres SESSION CLOSED successfully [OK]"
                print(ok_log) if self.logging_ok_ops else None
        except Exception as error:
            print(f"Postgres SESSION CLOSING error [ERROR]:\n"
                  f"error: {error}")
            raise
