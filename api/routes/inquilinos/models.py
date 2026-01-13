from sqlalchemy.dialects.mysql import CHAR as MYSQL_CHAR
from api.contrib.models import BaseModel
from sqlalchemy import Integer, String, CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship


class InquilinoModel(BaseModel):
    __tablename__ = 'inquilinos'

    pk_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(50), nullable=False)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    data_nascimento: Mapped[str] = mapped_column(String(10), nullable=False)

    rg: Mapped[str] = mapped_column(String(15), unique=False, nullable=True)
    orgao_emissor: Mapped[str] = mapped_column(String(50), nullable=True)
    estado_civil: Mapped[str] = mapped_column(String(25), nullable=False)
    profissao_ocupacao: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nome_pai: Mapped[str] = mapped_column(String(50), nullable=False)
    nome_mae: Mapped[str] = mapped_column(String(50), nullable=False)

    contratos: Mapped[list['ContratoModel']] = relationship(back_populates='inquilino', lazy='selectin')

    tenant_id: Mapped[CHAR] = mapped_column(MYSQL_CHAR(36), nullable=False)
