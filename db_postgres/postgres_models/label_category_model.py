from typing import Optional, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_postgres.postgres_conn_async.pgs_async_connection import Base
from db_postgres.postgres_models.orm_models_fields_mixins import (
    ActiveMix, CreateUpdateMix, CreateReasonMix)


class LabelCategoryModel(Base, CreateReasonMix, ActiveMix, CreateUpdateMix):
    __tablename__ = "label_category"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("dataset.id"))

    label_index: Mapped[int] = mapped_column(unique=True)
    category_name: Mapped[str] = mapped_column(unique=True)

    # rel_labels_texts: Mapped[List["LabelTextModel"]] = relationship(
    #     argument="LabelTextModel",
    #     # order_by="LabelTextModel.label_index_hint",
    #     back_populates="rel_label_category")
