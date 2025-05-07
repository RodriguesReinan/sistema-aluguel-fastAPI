from sqlalchemy import String, DateTime, CHAR, Integer
from datetime import datetime
from sqlalchemy.dialects.mysql import CHAR as MYSQL_CHAR
from api.contrib.models import BaseModel
from sqlalchemy.orm import Mapped, mapped_column


class LogModel(BaseModel):
    __tablename__ = "tables_logs"
    pk_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[str] = mapped_column(String(50), nullable=False)  # Quem fez a ação
    acao: Mapped[str] = mapped_column(String(50), nullable=False)        # Criou, Atualizou, Deletou
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)  # Descrição amigável
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    tenant_id: Mapped[CHAR] = mapped_column(MYSQL_CHAR(36), nullable=False)
