from pydantic import Field
from typing import Annotated, Literal
from datetime import datetime

from api.contrib.schemas import BaseSchema, OutMixin
from api.routes.contratos.schemas import Contrato


class Notificacao(BaseSchema):
    tipo_notificacao: Annotated[Literal['atraso', 'vencimento'], Field(description='Tipo de notificação')]
    data_envio: Annotated[datetime, Field(description='Data de envio da notificação')]
    meio_envio: Annotated[Literal['email', 'whatsapp', 'push', 'sms'], Field(description='Forma de envio da notificação')]
    titulo: Annotated[str, Field(description='Título da notificação', max_length=75)]
    mensagem: Annotated[str, Field(description='Mensagem enviada no corpo da notificação', max_length=500)]
    status: Annotated[Literal['pendente', 'enviado-visualizado', 'erro', 'enviado-nao-visualizado'], Field(description='Status do envio da notificação')]
    pagamento_id: Annotated[int, Field(description='id do contrato de aluguel')]
    usuario_id: Annotated[int, Field(description='id do usuario que criou o contrato')]


class NotificacaoIn(Notificacao):
    dispositivo_token: Annotated[str, Field(description='Token do dispositivo que recebeu a notificação')]


class NotificacaoContrato(BaseSchema):
    cpf: Annotated[str, Field(description='CPF do inquilino', example='99999999999', max_length=11)]


class NotificacaoOut(Notificacao, OutMixin):
    pass


