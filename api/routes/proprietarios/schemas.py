from pydantic import Field, field_validator
from typing import Annotated, Optional
from api.contrib.schemas import BaseSchema, OutMixin


class Proprietario(BaseSchema):
    nome: Annotated[str, Field(description='Nome do proprietário', example='Reinan Rodrigues', max_length=50)]
    cpf: Annotated[str, Field(description='CPF do proprietário', example='99999999999', max_length=11)]
    telefone: Annotated[str, Field(description='Telefone do proprietário', example='61996996152', max_length=20)]
    endereco: Annotated[str, Field(description='Endereço do proprietário',
                                   example='Quadra 202, L. 11, C. 25, São Sebastião-DF', max_length=255)]
    conta_bancaria: Annotated[Optional[str], Field(None, description='Conta bancária do proprietário',
                                                   example='Ag. 0001, conta: 332548-0, Banco: Inter', max_length=50)]
    pix: Annotated[Optional[str], Field(None, description='Pix do proprietário', example='04317985168', max_length=50)]
    chave_pix: Annotated[Optional[str], Field(None, description='Chave pix do proprietário', example='CPF',
                                              max_length=20)]

    rg: Annotated[str, Field(description='RG do proprietário', example='99999999', max_length=15)]
    orgao_emissor: Annotated[str, Field(description='Órgão Emissor do RG', example='SSP/DF', max_length=50)]
    estado_civil: Annotated[str, Field(description='Estado civil do proprietário', example='Solteiro', max_length=25)]
    profissao_ocupacao: Annotated[str, Field(description='Profissão/Ocupação do proprietário',
                                             example='Servidor Público', max_length=50)]
    email: Annotated[str, Field(description='E-mail do proprietário', example='proprietario@gmail.com', max_length=50)]

    @field_validator('*')
    def check_empty_strings(cls, value, info):
        if isinstance(value, str) and value.strip() == "":
            raise ValueError(f"O campo '{info.field_name}' não pode ser vazio.")
        return value


class ProprietarioImovel(BaseSchema):
    cpf: Annotated[str, Field(description='CPF do proprietário', example='99999999999', max_length=11)]


class ProprietarioIn(Proprietario):
    pass


class ProprietarioOut(Proprietario, OutMixin):
    pass


class ProprietarioUpdate(BaseSchema):
    nome: Annotated[Optional[str], Field(None, description='Nome do proprietário', example='Reinan', max_length=25)]
    telefone: Annotated[Optional[str], Field(None, description='Telefone do proprietário', example='61996996151',
                                             max_length=20)]
    endereco: Annotated[Optional[str], Field(None, description='Endereço do proprietário', example='qn 23',
                                             max_length=255)]
    conta_bancaria: Annotated[Optional[str], Field(None, description='Conta bancária do proprietário', example='3001',
                                                   max_length=50)]
    pix: Annotated[Optional[str], Field(None, description='Pix do atleta', example='61996458', max_length=50)]
    chave_pix: Annotated[Optional[str], Field(None, description='Chave pix do proprietário', example='celular',
                                              max_length=20)]
    estado_civil: Annotated[str, Field(description='Estado civil do proprietário', example='Solteiro', max_length=25)]
    profissao_ocupacao: Annotated[str, Field(description='Profissão/Ocupação do proprietário',
                                             example='Servidor Público', max_length=50)]
    email: Annotated[str, Field(description='E-mail do proprietário', example='proprietario@gmail.com', max_length=50)]
