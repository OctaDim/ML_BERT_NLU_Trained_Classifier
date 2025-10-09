from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from db_postgres.postgres_async_conn.pgs_async_connection import Base
from db_postgres.postgres_models.orm_models_fields_mixins import (
    ActiveMix, CreateUpdateMix)


class CustomerModel(Base, ActiveMix, CreateUpdateMix):
    __tablename__ = "customer"
    __table_args__ = (
        UniqueConstraint("account_username", "account_id",
                         name="uq_username_account_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    account_username: Mapped[Optional[str]] = mapped_column()
    account_id: Mapped[Optional[str]] = mapped_column()

    # category_services: Mapped['Service'] = relationship(
    #     argument='Service',
    #     order_by='Service.name',
    #     back_populates="service_categories")
    #
    # category_masters: Mapped['Master'] = relationship(
    #     argument='Master',
    #     order_by='Master.full_name',
    #     back_populates="master_categories")
