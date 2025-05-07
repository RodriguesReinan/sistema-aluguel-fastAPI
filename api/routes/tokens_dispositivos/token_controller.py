from fastapi import APIRouter, status, Depends
from api.routes.tokens_dispositivos.schemas import TokenSchameIn, TokenSchemaOut
from api.services.token_disp_service import (register_token)
from api.contrib.dependecies import DatabaseDependency
from api.routes.usuarios.dependecies import get_current_user
from api.routes.usuarios.schemas.usuario_schema import UserOut


router = APIRouter()


@router.post(
    "/register-token",
    summary='Registrar um token do aparelho para receber notificação push',
    status_code=status.HTTP_201_CREATED,
    response_model=TokenSchemaOut
)
async def registrar_token(db_ession: DatabaseDependency, token_data: TokenSchameIn, current_user: UserOut = Depends(get_current_user)):
    return await register_token(db_ession, token_data)
