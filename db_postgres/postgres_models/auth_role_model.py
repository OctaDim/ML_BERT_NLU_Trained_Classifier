from enum import Enum
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from db_postgres.postgres_async_conn.pgs_async_connection import Base
from db_postgres.postgres_models.orm_models_fields_mixins import (
    ActiveMix, CreateUpdateMix)


class UserRole(Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"


class AuthRoleModel(Base, ActiveMix, CreateUpdateMix):
    __tablename__ = "admin_auth_role"
    __table_args__ = (UniqueConstraint(
        "auth_username", "auth_hashed_password",
        name="uq_auth_username_account_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    auth_username: Mapped[Optional[str]] = mapped_column(unique=True)
    auth_hashed_password: Mapped[Optional[str]] = mapped_column()
    auth_role: Mapped[Optional[UserRole]] = mapped_column(
        default=UserRole.USER)
