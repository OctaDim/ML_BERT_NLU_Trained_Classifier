from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column


class ActiveMixin:
    __abstract__ = True
    active: Mapped[Optional[bool]] = mapped_column(default=True)


class CreateUpdateMixin:
    __abstract__ = True
    created_at: Mapped[Optional[datetime]] = mapped_column(default=datetime.now)
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=datetime.now)


class StatusMixin:
    __abstract__ = True
    status: Mapped[Optional[str]] = mapped_column()
