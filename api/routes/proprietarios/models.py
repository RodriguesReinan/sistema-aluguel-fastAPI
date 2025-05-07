from sqlalchemy.dialects.mysql import CHAR as MYSQL_CHAR
from api.contrib.models import BaseModel
from sqlalchemy import Integer, String, CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ProprietarioModel(BaseModel):
    __tablename__ = 'proprietarios'

    pk_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(50), nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)

    rg: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    orgao_emissor: Mapped[str] = mapped_column(String(50), nullable=False)
    estado_civil: Mapped[str] = mapped_column(String(25), nullable=True)
    profissao_ocupacao: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    endereco: Mapped[str] = mapped_column(String(255), nullable=False)

    conta_bancaria: Mapped[str] = mapped_column(String(75), nullable=True)
    pix: Mapped[str] = mapped_column(String(50), nullable=True)
    chave_pix: Mapped[str] = mapped_column(String(20), nullable=True)

    imoveis: Mapped[list['ImovelModel']] = relationship(back_populates='proprietario', lazy='selectin')

    tenant_id: Mapped[CHAR] = mapped_column(MYSQL_CHAR(36), nullable=False)
