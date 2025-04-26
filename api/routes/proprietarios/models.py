from datetime import datetime

from api.contrib.models import BaseModel
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ProprietarioModel(BaseModel):
    __tablename__ = 'proprietarios'

    pk_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(50), nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)

    rg: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    orgao_emissor: Mapped[str] = mapped_column(String(50), nullable=False)
    estado_civil: Mapped[str] = mapped_column(String(25), nullable=False)
    profissao_ocupacao: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    endereco: Mapped[str] = mapped_column(String(255))
    conta_bancaria: Mapped[str] = mapped_column(String(50))
    pix: Mapped[str] = mapped_column(String(50))
    chave_pix: Mapped[str] = mapped_column(String(20))

    imoveis: Mapped[list['ImovelModel']] = relationship(back_populates='proprietario', lazy='selectin')
