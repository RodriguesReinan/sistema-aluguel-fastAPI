import uuid
from sqlalchemy import CHAR

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.mysql import CHAR as MYSQL_CHAR
from sqlalchemy import DateTime, Boolean
from typing import Optional
from datetime import datetime


class BaseModel(DeclarativeBase):
    id: Mapped[CHAR] = mapped_column(MYSQL_CHAR(36), default=lambda: str(uuid.uuid4()), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                                                 nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ativo: Mapped[Boolean] = mapped_column(Boolean, default=True)

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
        self.ativo = False

    def restore(self):
        self.deleted_at = None
        self.ativo = True
