from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
from api.contrib.models import BaseModel


class TokenDispositivoModel(BaseModel):
    __tablename__ = "tokens_dispositivos"

    pk_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dispositivo_token: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    # criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    usuario: Mapped['UsuarioModel'] = relationship(back_populates="tokens", lazy='selectin')
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.pk_id"),
                                            nullable=False)  # Relacionado ao usuário (proprietário/corretor)
