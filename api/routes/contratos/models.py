from datetime import date
from api.contrib.models import BaseModel
from sqlalchemy import Integer, Float, Date, ForeignKey, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

# from api.routes.usuarios.models.usuario_model import UsuarioModel


class ContratoModel(BaseModel):
    __tablename__ = 'contratos'

    pk_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[date] = mapped_column(Date, nullable=False)
    dia_vencimento: Mapped[int] = mapped_column(Integer, nullable=False)
    valor_mensal: Mapped[float] = mapped_column(Float, nullable=False)
    taxa_limpeza: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(Enum("ativo", "encerrado", "pendente", name="status_enum"), nullable=False)

    imovel: Mapped['ImovelModel'] = relationship(back_populates='contratos', lazy='selectin')
    imovel_id: Mapped[int] = mapped_column(ForeignKey('imoveis.pk_id'), nullable=False)

    inquilino: Mapped['InquilinoModel'] = relationship(back_populates='contratos', lazy='selectin')
    inquilino_id: Mapped[int] = mapped_column(ForeignKey('inquilinos.pk_id'), nullable=False)

    pagamentos: Mapped['PagamentoModel'] = relationship(back_populates='contratos')

    usuario: Mapped['UsuarioModel'] = relationship(back_populates='contratos', lazy='selectin')
    usuario_id: Mapped[int] = mapped_column(ForeignKey('usuarios.pk_id'), nullable=False)
