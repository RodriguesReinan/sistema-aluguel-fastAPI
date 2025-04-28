from datetime import datetime
from api.contrib.models import BaseModel
from sqlalchemy import Integer, String, Float, CHAR, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import CHAR as MYSQL_CHAR


class ImovelModel(BaseModel):
    __tablename__ = 'imoveis'

    pk_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    endereco: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    area_total: Mapped[float] = mapped_column(Float)
    qtd_quartos: Mapped[int] = mapped_column(Integer)
    qtd_suites: Mapped[int] = mapped_column(Integer)
    qtd_banheiros: Mapped[int] = mapped_column(Integer)
    descricao: Mapped[str] = mapped_column(String(500))

    aluguel_venda: Mapped[str] = mapped_column(
        Enum("aluguel", "venda", name="alugel_ou_venda"), default="Selecione", nullable=False)
    casa_apartamento: Mapped[str] = mapped_column(
        Enum("casa", "apartamento", name="casa_ou_apartamento"), default="Selecione", nullable=False)
    tipo_imovel: Mapped[str] = mapped_column(
        Enum("residencial", "comercial", name="tipo_imovel"), default="Selecione", nullable=False)

    proprietario: Mapped['ProprietarioModel'] = relationship(back_populates='imoveis', lazy='selectin')
    proprietario_id: Mapped[int] = mapped_column(ForeignKey('proprietarios.pk_id'), nullable=False)

    contratos: Mapped[list['ContratoModel']] = relationship(back_populates='imovel', lazy='selectin')

    tenant_id: Mapped[CHAR] = mapped_column(MYSQL_CHAR(36), nullable=False)
