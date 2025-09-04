from datetime import datetime
from typing import Optional

# from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db_postgres.postgres_async_conn.pgs_async_connection import Base


class TrainedModelModel(Base):
    __tablename__ = "trained_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    # dataset_id: Mapped[int] = mapped_column(ForeignKey("dataset.id"))

    last_saved_directory: Mapped[str] = mapped_column()
    dataset_name: Mapped[str] = mapped_column()

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
