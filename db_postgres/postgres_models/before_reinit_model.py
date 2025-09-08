from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db_postgres.postgres_async_conn.pgs_async_connection import Base


class BeforeReinitModel(Base):
    __tablename__ = "before_reinit_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"),
                                             nullable=True)

    temp_model_dir: Mapped[str] = mapped_column()
    dataset_name: Mapped[str] = mapped_column(nullable=True)
    labels_before: Mapped[int] = mapped_column(nullable=True)
    labels_after: Mapped[int] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=True)

    created: Mapped[datetime] = mapped_column(default=datetime.now(),
                                              nullable=True)
    updated: Mapped[datetime] = mapped_column(onupdate=datetime.now(),
                                              nullable=True)
