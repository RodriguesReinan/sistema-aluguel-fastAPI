from fastapi import APIRouter, status
from api.routes.tokens_dispositivos.schemas import TokenSchameIn, TokenSchemaOut
from api.services.token_disp_service import (register_token)
from api.contrib.dependecies import DatabaseDependency


router = APIRouter()


@router.post(
    "/register-token",
    summary='Registrar um token do aparelho para receber notificação push',
    status_code=status.HTTP_201_CREATED,
    response_model=TokenSchemaOut
)
async def registrar_token(db_ession: DatabaseDependency, token_data: TokenSchameIn):
    return await register_token(db_ession, token_data)
