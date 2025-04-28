from datetime import datetime
from api.contrib.models import BaseModel
from sqlalchemy import Integer, String, CHAR, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import CHAR as MYSQL_CHAR


class NotificacaoModel(BaseModel):
    __tablename__ = 'notificacoes'

    pk_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    pagamento_id: Mapped[int] = mapped_column(ForeignKey('pagamentos.pk_id'), nullable=False)
    pagamento: Mapped['PagamentoModel'] = relationship(back_populates='notificacoes', lazy='selectin')

    usuario_id: Mapped[int] = mapped_column(ForeignKey('usuarios.pk_id'), nullable=False)  # 👈 Novo campo
    usuario: Mapped['UsuarioModel'] = relationship(back_populates='notificacoes', lazy='selectin')  # 👈 Relacionamento

    tipo_notificacao: Mapped[str] = mapped_column(
        Enum("vencimento", "atraso", "outro", name="tipo_notificacao"),
        nullable=False)

    data_envio: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    meio_envio: Mapped[str] = mapped_column(
        Enum("email", "whatsApp", "push", name="meio_notificacao"),
        nullable=False)

    titulo: Mapped[str] = mapped_column(String(75), nullable=False)
    mensagem: Mapped[str] = mapped_column(String(500), nullable=False)

    status: Mapped[str] = mapped_column(
        Enum("pendente", "enviado-nao-visualizado", "erro", "enviado-visualizado", name="status_notificacao"),
        default="pendente", nullable=False)

    tenant_id: Mapped[CHAR] = mapped_column(MYSQL_CHAR(36), nullable=False)
