from fastapi import APIRouter, status, Depends
from api.routes.inquilinos.schemas import InquilinoIn, InquilinoOut, InquilinoUpdate
from api.services.inquilino_service import (create_inquilino, get_all_inquilinos, get_inquilino, patch_inquilino,
                                            delete_inquilino)
from api.contrib.dependecies import DatabaseDependency
from api.routes.usuarios.dependecies import get_current_user
from api.routes.usuarios.models.usuario_model import UsuarioModel


router = APIRouter()


@router.post(
    "/",
    summary='Criar um novo inquilino',
    status_code=status.HTTP_201_CREATED,
    response_model=InquilinoOut
)
async def criar_inquilino(inquilino: InquilinoIn, db_session: DatabaseDependency,
                          current_user: UsuarioModel = Depends(get_current_user)):
    return await create_inquilino(db_session, current_user, inquilino)


@router.get(
    path='/',
    summary='Consultar todos os inquilinos',
    status_code=status.HTTP_200_OK,
    response_model=list[InquilinoOut],
)
async def listar_inquilinos(db_session: DatabaseDependency, current_user: UsuarioModel = Depends(get_current_user)):
    return await get_all_inquilinos(db_session, current_user)


@router.get(
    path='/{id}',
    summary='Consultar um inquilino',
    status_code=status.HTTP_200_OK,
    response_model=InquilinoOut,
)
async def listar_inquilino_id(id:str, db_session: DatabaseDependency, current_user: UsuarioModel = Depends(get_current_user)):
    return await get_inquilino(id, db_session, current_user)


@router.patch(
    '/{id}',
    summary='Editar um inquilino pelo id.',
    status_code=status.HTTP_200_OK,
    response_model=InquilinoOut,
)
async def editar_inquilino(
        id:str,
        db_session: DatabaseDependency,
        inquilino_up: InquilinoUpdate,
        current_user: UsuarioModel = Depends(get_current_user),
):
    return await patch_inquilino(id, db_session, inquilino_up, current_user)


@router.delete(
    '/{id}',
    summary='Deletar um inquilino pelo id.',
    status_code=status.HTTP_204_NO_CONTENT
)
async def deletar_inquilino(id:str,
                            db_session: DatabaseDependency,
                            current_user: UsuarioModel = Depends(get_current_user)):
    return await delete_inquilino(id, db_session, current_user)
