from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime
from api.contrib.models import BaseModel


class UsuarioModel(BaseModel):
    __tablename__ = "usuarios"

    pk_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    # created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    tokens: Mapped[list['TokenDispositivoModel']] = relationship(back_populates="usuario", lazy='selectin')

    contratos: Mapped[list['ContratoModel']] = relationship(back_populates='usuario', lazy='selectin')

    notificacoes: Mapped[list['NotificacaoModel']] = relationship(back_populates='usuario', lazy='selectin')


# class TokenBlacklist(BaseModel):
#     __tablename__ = "token_blacklist"
#     token: Mapped[str] = mapped_column(String(100), primary_key=True)
#     expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
