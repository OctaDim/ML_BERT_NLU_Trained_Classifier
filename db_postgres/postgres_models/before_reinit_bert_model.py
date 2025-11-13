from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db_postgres.postgres_init.declarative_base_model import Base
from db_postgres.postgres_models.orm_models_fields_mixins import (
    CreateUpdateMix, CreateReasonMix)


class BeforeReinitBertModel(Base, CreateReasonMix, CreateUpdateMix):
    __tablename__ = "before_reinit_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("dataset.id"))

    customer_id: Mapped[Optional[int]] = mapped_column()
    dataset_name: Mapped[Optional[str]] = mapped_column()

    temp_model_dir: Mapped[str] = mapped_column()
    labels_before: Mapped[Optional[int]] = mapped_column()
    labels_after: Mapped[Optional[int]] = mapped_column()
