from fastapi import APIRouter, status, Depends
from api.routes.proprietarios.schemas import ProprietarioIn, ProprietarioOut, ProprietarioUpdate
from api.services.proprietario_service import (create_proprietario, get_all_proprietarios, get_proprietario,
                                               patch_proprietario, delete_proprietario)
from api.contrib.dependecies import DatabaseDependency
from api.routes.usuarios.dependecies import get_current_user
from api.routes.usuarios.models.usuario_model import UsuarioModel


router = APIRouter()


@router.post(
    "/",
    summary='Criar um novo proprietário',
    status_code=status.HTTP_201_CREATED,
    response_model=ProprietarioOut
)
async def criar_proprietario(proprietario: ProprietarioIn, db_session: DatabaseDependency,
                             current_user: UsuarioModel = Depends(get_current_user)):
    return await create_proprietario(db_session, current_user, proprietario)


@router.get(
    path='/',
    summary='Consultar todos os proprietario',
    status_code=status.HTTP_200_OK,
    response_model=list[ProprietarioOut],
)
async def listar_proprietarios(db_session: DatabaseDependency, current_user: UsuarioModel = Depends(get_current_user)):
    return await get_all_proprietarios(db_session, current_user)


@router.get(
    path='/{id}',
    summary='Consultar um proprietario',
    status_code=status.HTTP_200_OK,
    response_model=ProprietarioOut,
)
async def listar_proprietario_id(id:str, db_session: DatabaseDependency,
                                 current_user: UsuarioModel = Depends(get_current_user)):
    return await get_proprietario(id, db_session, current_user)


@router.patch(
    '/{id}',
    summary='Editar um proprietário pelo id.',
    status_code=status.HTTP_200_OK,
    response_model=ProprietarioOut,
)
async def editar_proprietario(id:str, db_session: DatabaseDependency, proprietario_up: ProprietarioUpdate,
                              current_user: UsuarioModel = Depends(get_current_user)):
    return await patch_proprietario(id, db_session, proprietario_up, current_user)


@router.delete(
    '/{id}',
    summary='Deletar um proprietário pelo id.',
    status_code=status.HTTP_204_NO_CONTENT
)
async def deletar_proprietario(id:str, db_session: DatabaseDependency, current_user: UsuarioModel = Depends(get_current_user)):
    return await delete_proprietario(id, db_session, current_user)
