from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db_postgres.postgres_init.declarative_base_model import Base
from db_postgres.postgres_models.orm_models_fields_mixins import (
    ActiveMix, CreateUpdateMix, CreateReasonMix)


class RenamedCustomerClassModel(Base, ActiveMix,
                                CreateReasonMix, CreateUpdateMix):
    __tablename__ = "renamed_customer_class"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    label_category_id: Mapped[int] = mapped_column(ForeignKey("label_category.id"))

    # account_id: Mapped[str] = mapped_column()
    # account_username: Mapped[str] = mapped_column()
    renamed_class_name: Mapped[str] = mapped_column()
