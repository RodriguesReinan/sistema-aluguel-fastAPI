from pydantic import Field, PositiveFloat, field_validator
from typing import Annotated, Optional, Literal
from api.contrib.schemas import BaseSchema, OutMixin
from api.routes.proprietarios.schemas import ProprietarioImovel
from api.routes.imoveis.models import ImovelModel


class Imovel(BaseSchema):
    endereco: Annotated[str, Field(description='Endereço do imóvel',
                                   example='Quadra 202, L. 11, C. 25, São Sebastião-DF', max_length=255)]
    area_total: Annotated[Optional[float], Field(None, description='Área total do imóvel', example=70.5)]
    qtd_quartos: Annotated[Optional[int], Field(None, description='Quantidade de quartos do imóvel', example=2)]
    qtd_suites: Annotated[Optional[int], Field(None, description='Quantidade de suítes do imóvel', example=1)]
    qtd_banheiros: Annotated[Optional[int], Field(None, description='Quantidade de banheiros do imóvel', example=2)]
    descricao: Annotated[Optional[str], Field(None, description='Descrição do imóvel',
                                              example='Ótima localização, próximo à parada de ônibus.', max_length=500)]

    aluguel_venda: Annotated[Literal['aluguel', 'venda'], Field(description='Tipo de imóvel - Aluguel ou Venda')]
    casa_apartamento: Annotated[Literal['casa', 'apartamento'], Field(description='Tipo de imóvel - casa ou AP')]
    tipo_imovel: Annotated[Literal['residencial', 'comercial'], Field(description='Tipo de imóvel - residencial '
                                                                                  'ou comercial')]

    proprietario: Annotated[ProprietarioImovel, Field(description='Proprietário do imóvel')]

    @field_validator('*')
    def check_empty_strings(cls, value, info):
        if isinstance(value, str) and value.strip() == "":
            raise ValueError(f"O campo '{info.field_name}' não pode ser vazio.")
        return value


class ImovelContrato(OutMixin):
    endereco: Annotated[str, Field(description='Endereço do imóvel',
                                   example='Quadra 202, L. 11, C. 25, São Sebastião-DF', max_length=255)]
    numero: Optional[str] = None
    bairro: Optional[str] = None

    @classmethod
    def from_model(cls, model: ImovelModel) -> "ImovelContrato":
        partes = model.endereco.split(',')

        numero = partes[2].strip() if len(partes) > 2 else ''
        bairro = partes[3].strip() if len(partes) > 3 else ''

        return cls(
            id=model.id,
            endereco=model.endereco,
            numero=numero,
            bairro=bairro
        )


class ImovelIn(Imovel):
    pass


class ImovelOut(Imovel, OutMixin):
    pass


class ImovelUpdate(BaseSchema):
    area_total: Annotated[Optional[float], Field(None, description='Área total do imóvel', example=70.5)]
    qtd_quartos: Annotated[Optional[int], Field(None, description='Quantidade de quartos do imóvel', example=2)]
    qtd_suites: Annotated[Optional[int], Field(None, description='Quantidade de suítes do imóvel', example=1)]
    qtd_banheiros: Annotated[Optional[int], Field(None, description='Quantidade de banheiros do imóvel', example=2)]
    descricao: Annotated[Optional[str], Field(None, description='Descrição do imóvel',
                                              example='Ótima localização, próximo à parada de ônibus.', max_length=500)]

    proprietario: Annotated[Optional[ProprietarioImovel], Field(None, description='Proprietário do imóvel')]
