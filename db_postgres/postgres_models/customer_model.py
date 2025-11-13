from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from db_postgres.postgres_init.declarative_base_model import Base
from db_postgres.postgres_models.orm_models_fields_mixins import (
    ActiveMix, CreateUpdateMix, CreateReasonMix)


class CustomerModel(Base, ActiveMix, CreateUpdateMix, CreateReasonMix):
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

    @hybrid_property
    def account_data(self):
        username_str = self.account_username or "_____"
        id_str = self.account_id or "___"
        field_value = f"{username_str} / {id_str}"
        return field_value
