from datetime import date

from pydantic import Field, PositiveFloat
from typing import Annotated, Optional, Literal
from api.contrib.schemas import BaseSchema, OutMixin
from api.routes.inquilinos.schemas import InquilinoContrato
from api.routes.imoveis.schemas import ImovelContrato
from api.routes.usuarios.schemas.usuario_schema import UsuarioContrato
from api.routes.contratos.models import ContratoModel
from api.routes.inquilinos.models import InquilinoModel
from api.routes.imoveis.models import ImovelModel
from api.routes.usuarios.models.usuario_model import UsuarioModel


class Contrato(BaseSchema):
    data_inicio: Annotated[date, Field(description='Data início do contratos de aluguel', example='2025-03-05')]
    data_fim: Annotated[date, Field(description='Data final do contratos de aluguel', example='2026-03-05')]
    dia_vencimento: Annotated[int, Field(ge=1, le=31, description='Dia de vencimento do aluguel, de cada mês',
                                          example='10')]
    valor_mensal: Annotated[PositiveFloat, Field(description='Valor mensal do aluguel em reais', example=750.00)]
    taxa_limpeza: Annotated[PositiveFloat, Field(description='Taxa de limpeza do imóvel em reais', example=50.00)]
    status: Annotated[Literal["ativo", "encerrado", "pendente"], Field(description='Status do contratos')]

    inquilino: Annotated[InquilinoContrato, Field(description='Inquilino do imóvel')]
    imovel: Annotated[ImovelContrato, Field(description='Imóvel a ser alugado')]
    usuario: Annotated[UsuarioContrato, Field(description='Usuário logado no sistema')]
    # usuario_id: Annotated[int, Field(description='Usuário logado no sistema')]


class ContratoIn(Contrato):
    pass


class ContratoOut(Contrato, OutMixin):
    # pass
    @classmethod
    def from_model(cls, contrato: ContratoModel, inquilino: InquilinoModel,
                   imovel: ImovelModel, usuario: UsuarioModel) -> "ContratoOut":
        return cls(
            id=contrato.id,
            data_inicio=contrato.data_inicio,
            data_fim=contrato.data_fim,
            dia_vencimento=contrato.dia_vencimento,
            valor_mensal=contrato.valor_mensal,
            taxa_limpeza=contrato.taxa_limpeza,
            status=contrato.status,
            inquilino=InquilinoContrato.from_orm(inquilino),
            imovel=ImovelContrato.from_model(imovel),
            usuario=UsuarioContrato.from_orm(usuario),
        )


class ContratoPagamento(OutMixin):
    pass


class ContratoUpdate(BaseSchema):
    data_fim: Annotated[Optional[date], Field(description='Data final do contratos de aluguel', example='2026-03-05')]
    dia_vencimento: Annotated[Optional[int], Field(description='Dia de vencimento do aluguel, de cada mês', example='10')]
    valor_mensal: Annotated[Optional[PositiveFloat], Field(description='Valor mensal do aluguel em reais', example=750.00)]
    status: Annotated[Optional[Literal["ativo", "encerrado", "pendente"]], Field(description='Status do contratos')]
    taxa_limpeza: Annotated[Optional[PositiveFloat], Field(description='Taxa de limpeza do imóvel em reais', example=50.00)]

