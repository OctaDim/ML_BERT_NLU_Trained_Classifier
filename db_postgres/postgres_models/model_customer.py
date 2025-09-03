from datetime import datetime
from typing import Optional

# from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db_postgres.postgres_async_conn.pgs_async_connection import Base


class Customer(Base):
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[Optional[str]]
    account_id: Mapped[Optional[str]]

    active: Mapped[bool] = mapped_column(default=True)
    created: Mapped[datetime] = mapped_column(default=datetime.now(),
                                              nullable=True)
    updated: Mapped[datetime] = mapped_column(onupdate=datetime.now(),
                                              nullable=True)

    # category_services: Mapped['Service'] = relationship(
    #     argument='Service',
    #     order_by='Service.name',
    #     back_populates="service_categories")
    #
    # category_masters: Mapped['Master'] = relationship(
    #     argument='Master',
    #     order_by='Master.full_name',
    #     back_populates="master_categories")
