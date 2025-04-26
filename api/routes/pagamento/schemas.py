from datetime import date

from pydantic import Field, PositiveFloat
from typing import Annotated, Optional, Literal
from api.contrib.schemas import BaseSchema, OutMixin
from api.routes.contratos.schemas import ContratoPagamento


class Pagamento(BaseSchema):
    valor_pago: Annotated[Optional[float], Field(description='Valor que o inquilino pagou', example='750,00')]
    data_vencimento: Annotated[date, Field(description='Data de vencimento do contrato de aluguel',
                                           example='2026-03-05')]
    data_pagamento: Annotated[Optional[date], Field(description='Data de pagamento do aluguel', example='2026-04-10')]
    metodo_pagamento: Annotated[Optional[Literal['PIX', 'Boleto', 'transferência']],
                                Field(None, description='Método de pagamento do contrato')]
    # metodo_pagamento: Annotated[Optional[str], Field(description='Método de pagamento do contrato')]
    status: Annotated[Literal["pago", "pago parcialmente", "pendente", "atrasado"],
                      Field(description='Status de pagamento do contrato')]

    contratos: Annotated[ContratoPagamento, Field(description='id do contrato de aluguel')]


class PagamentoIn(Pagamento):
    pass


class PagamentoOut(Pagamento, OutMixin):
    pass


class PagamentoUpdate(BaseSchema):
    valor_pago: Annotated[Optional[float], Field(None, description='Valor que o inquilino pagou', example=750.00)]
    data_vencimento: Annotated[Optional[date], Field(None, description='Data de vencimento do contrato de aluguel', example='2026-03-05')]
    data_pagamento: Annotated[Optional[date], Field(None, description='Data de pagamento do aluguel', example='2026-04-10')]
    metodo_pagamento: Annotated[Optional[Literal['PIX', 'Boleto', 'transferência']],
                                Field(None, description='Método de pagamento do contrato')]
    status: Annotated[Optional[Literal["pago", "pago parcialmente", "pendente", "atrasado"]],
                      Field(None, description='Status de pagamento do contrato')]

