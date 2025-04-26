from pydantic import Field
from typing import Annotated, Optional
from datetime import date

from api.contrib.schemas import BaseSchema, OutMixin
from api.routes.usuarios.schemas.usuario_schema import UserTokenDispositivo


class TokenSchema(BaseSchema):
    dispositivo_token: Annotated[str, Field(description='Token do dispositivo que recebeu a notificação')]
    usuario: Annotated[UserTokenDispositivo, Field(description='id do usuário')]


class TokenSchameIn(TokenSchema):
    pass


class TokenSchemaOut(TokenSchema, OutMixin):
    pass
