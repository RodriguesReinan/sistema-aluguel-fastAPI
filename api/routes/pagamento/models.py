from datetime import date
from api.contrib.models import BaseModel
from sqlalchemy import Integer, String, Float, Date, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PagamentoModel(BaseModel):
    __tablename__ = 'pagamentos'

    pk_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    valor_pago: Mapped[float] = mapped_column(Float, nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False)
    data_pagamento: Mapped[date] = mapped_column(Date, nullable=True)
    metodo_pagamento: Mapped[str] = mapped_column(Enum('PIX', 'Boleto', 'transferência', name='metodo_pagamento'),
                                                  nullable=True)
    status: Mapped[str] = mapped_column(Enum("pago", "pendente", "atrasado", name="status_pagamento"), nullable=False)

    contratos: Mapped['ContratoModel'] = relationship(back_populates='pagamentos', lazy='selectin')
    contrato_id: Mapped[int] = mapped_column(ForeignKey('contratos.pk_id'), nullable=False)

    notificacoes: Mapped[list['NotificacaoModel']] = relationship(back_populates='pagamento')

