from pydantic import Field, field_validator, ValidationInfo
from typing import Annotated, Optional, Union, get_origin, get_args

from api.contrib.schemas import BaseSchema, OutMixin


class Inquilino(BaseSchema):
    nome: Annotated[str, Field(description='Nome do inquilino', example='Reinan', max_length=50)]
    cpf: Annotated[str, Field(description='CPF do inquilino', example='99999999999', max_length=11)]
    telefone: Annotated[str, Field(description='Telefone do inquilino', example='61996996152', max_length=20)]
    data_nascimento: Annotated[str, Field(description='Data de nascimento do inquilino', example='31/07/1993',
                                          max_length=10)]

    rg: Annotated[Optional[str], Field(None, description='RG do inquilino', example='99999999', max_length=15)]
    orgao_emissor: Annotated[Optional[str], Field(None, description='Órgão Emissor do RG', example='SSP-DF', max_length=50)]
    estado_civil: Annotated[str, Field(description='Estado civil do inquilino', example='Solteiro', max_length=25)]
    profissao_ocupacao: Annotated[str, Field(description='Profissão/Ocupação do inquilino',
                                             example='Vendedor', max_length=50)]
    email: Annotated[str, Field(description='E-mail do inquilino', example='inquilino@gmail.com', max_length=50)]
    nome_pai: Annotated[str, Field(description='Nome do pai do inquilino', example='José', max_length=50)]
    nome_mae: Annotated[str, Field(description='Nome da mãe do inquilino', example='Maria', max_length=50)]

    @field_validator('*', mode='before')
    def check_empty_strings(cls, value, info: ValidationInfo):
        # verifica se a string é vazia
        if isinstance(value, str) and value.strip() == "":
            # verifica se o campo é opcional
            field_name = info.field_name
            annotation = cls.model_fields[field_name].annotation
            is_optional = get_origin(annotation) is Union and type(None) in get_args(annotation)

            if is_optional:
                return None  # converte string vazia para None
            else:
                raise ValueError(f"O campo '{info.field_name}' não pode ser vazio.")
        return value


class InquilinoIn(Inquilino):
    pass


class InquilinoContrato(BaseSchema):
    cpf: Annotated[str, Field(description='CPF do inquilino', example='99999999999', max_length=11)]
    nome: Annotated[str, Field(description='Nome do inquilino', example='Reinan', max_length=50)]


class InquilinoOut(Inquilino, OutMixin):
    pass


class InquilinoUpdate(BaseSchema):
    nome: Annotated[
        Optional[str], Field(None, description='Nome do inquilino', example='Reinan', max_length=50)]
    telefone: Annotated[
        Optional[str], Field(None, description='Telefone do inquilino', example='61996996152', max_length=20)]
    estado_civil: Annotated[
        Optional[str], Field(None, description='Estado civil do inquilino', example='Solteiro', max_length=25)]
    profissao_ocupacao: Annotated[
        Optional[str], Field(None, description='Profissão/Ocupação do inquilino', example='Vendedor', max_length=50)]
    email: Annotated[
        Optional[str], Field(None, description='E-mail do inquilino', example='inquilino@gmail.com', max_length=50)]
