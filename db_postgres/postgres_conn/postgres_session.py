from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine, async_sessionmaker, AsyncSession)
from sqlalchemy.orm import sessionmaker, Session


class PgsAsyncSession:
    def __init__(self, engine: AsyncEngine,
                 log_good_ops: bool = False):
        self.engine = engine
        self.AsyncSessionMaker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            info={"any_attribute": "any session available attribute data"}, )
        self.async_session = None
        self.logging_ok_ops = log_good_ops
        
    async def __aenter__(self) -> AsyncSession:
        try:
            self.async_session = self.AsyncSessionMaker()
            ok_log = f"Postgres ASYNC SESSION CREATED successfully [OK]"
            print(ok_log) if self.logging_ok_ops else None
            return self.async_session
        except Exception as error:
            print(f"Postgres ASYNC SESSION CREATING [ERROR]")
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if not exc_type:  # No session context manager error
            try:
                await self.async_session.commit()
                ok_log = f"Postgres ASYNC SESSION COMMIT success [OK]"
                print(ok_log) if self.logging_ok_ops else None
            except Exception as error:
                await self.async_session.rollback()
                print(f"Postgres ASYNC SESSION ROLLBACK "
                      f"(due to ASYNC SESSION COMMIT error) [ERROR]\n"
                      f"error: {error}")
                raise
        else:  # Session context manager error returned
            print(f"Postgres ASYNC SESSION CONTEXT MANAGER [ERROR]:\n"
                  f"exc_type: {exc_type}\n"
                  f"exc_val: {exc_val}\n"
                  f"exc_tb: {exc_tb}\n")
            try:
                await self.async_session.rollback()
                print(f"Postgres ASYNC SESSION ROLLBACK (due to session "
                      f"context manager inner error) [OK]\n")
            except Exception as error:
                print(f"Postgres ASYNC SESSION ROLLBACK (due to session "
                      f"context manager inner error) [ERROR]:\n"
                      f"error: {error}")
                raise
        try:
            if self.async_session.is_active:
                await self.async_session.close()
                ok_log = f"Postgres ASYNC SESSION CLOSED successfully [OK]"
                print(ok_log) if self.logging_ok_ops else None
        except Exception as error:
            print(f"Postgres SESSION ASYNC CLOSING error [ERROR]:\n"
                  f"error: {error}")
            raise


class PgsSyncSession:
    def __init__(self, engine: Engine,
                 log_good_ops: bool = False):
        self.engine = engine
        self.SessionMaker = sessionmaker(
            bind=self.engine,
            class_=Session,
            expire_on_commit=False,
            autoflush=False,
            info={"any_attribute": "any session available attribute data"}, )
        self.sync_session = None
        self.logging_ok_ops = log_good_ops

    def __enter__(self) -> Session:
        try:
            self.sync_session = self.SessionMaker()
            ok_log = f"Postgres SYNC SESSION CREATED successfully [OK]"
            print(ok_log) if self.logging_ok_ops else None
            return self.sync_session
        except Exception as error:
            print(f"Postgres SYNC SESSION CREATING [ERROR]")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if not exc_type:  # No session context manager error
            try:
                self.sync_session.commit()
                ok_log = f"Postgres SYNC SESSION COMMIT success [OK]"
                print(ok_log) if self.logging_ok_ops else None
            except Exception as error:
                self.sync_session.rollback()
                print(f"Postgres SYNC SESSION ROLLBACK "
                      f"(due to SESSION COMMIT error) [ERROR]\n"
                      f"error: {error}")
                raise
        else:  # Session context manager error returned
            print(f"Postgres SYNC SESSION CONTEXT MANAGER [ERROR]:\n"
                  f"exc_type: {exc_type}\n"
                  f"exc_val: {exc_val}\n"
                  f"exc_tb: {exc_tb}\n")
            try:
                self.sync_session.rollback()
                print(f"Postgres SYNC SESSION ROLLBACK (due to session "
                      f"context manager inner error) [OK]\n")
            except Exception as error:
                print(f"Postgres SYNC SESSION ROLLBACK (due to session "
                      f"context manager inner error) [ERROR]:\n"
                      f"error: {error}")
                raise
        try:
            if self.sync_session.is_active:
                self.sync_session.close()
                ok_log = f"Postgres SYNC SESSION CLOSED successfully [OK]"
                print(ok_log) if self.logging_ok_ops else None
        except Exception as error:
            print(f"Postgres SYNC SESSION CLOSING error [ERROR]:\n"
                  f"error: {error}")
            raise
