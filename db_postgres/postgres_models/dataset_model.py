from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db_postgres.postgres_async_conn.pgs_async_connection import Base
from db_postgres.postgres_models.orm_models_fields_mixins import (
    ActiveMix, CreateUpdateMix, CreateReasonMix)


class DatasetModel(Base, CreateReasonMix, ActiveMix, CreateUpdateMix):
    __tablename__ = "dataset"

    id: Mapped[int] = mapped_column(primary_key=True)

    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customer.id"))
    dataset_name: Mapped[str] = mapped_column(unique=True)
    dataset_csv_dir: Mapped[Optional[str]] = mapped_column(unique=True)

    # category_services: Mapped['Service'] = relationship(
    #     argument='Service',
    #     order_by='Service.name',
    #     back_populates="service_categories")
    #
    # category_masters: Mapped['Master'] = relationship(
    #     argument='Master',
    #     order_by='Master.full_name',
    #     back_populates="master_categories")
