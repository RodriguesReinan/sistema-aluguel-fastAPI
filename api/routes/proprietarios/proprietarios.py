from fastapi import APIRouter, status, Depends
from api.routes.proprietarios.schemas import ProprietarioIn, ProprietarioOut, ProprietarioUpdate
from api.services.proprietario_service import (create_proprietario, get_all_proprietarios, get_proprietario,
                                               patch_proprietario, delete_proprietario)
from api.contrib.dependecies import DatabaseDependency
from api.routes.usuarios.dependecies import get_current_user


router = APIRouter()


@router.post(
    "/",
    summary='Criar um novo proprietário',
    status_code=status.HTTP_201_CREATED,
    response_model=ProprietarioOut
)
async def criar_proprietario(proprietario: ProprietarioIn, db_session: DatabaseDependency,
                             ):
    return await create_proprietario(db_session, proprietario)


@router.get(
    path='/',
    summary='Consultar todos os proprietario',
    status_code=status.HTTP_200_OK,
    response_model=list[ProprietarioOut],
)
async def listar_proprietarios(db_session: DatabaseDependency):
    return await get_all_proprietarios(db_session)


@router.get(
    path='/{id}',
    summary='Consultar um proprietario',
    status_code=status.HTTP_200_OK,
    response_model=ProprietarioOut,
)
async def listar_proprietario_id(id:str, db_session: DatabaseDependency):
    return await get_proprietario(id, db_session)


@router.patch(
    '/{id}',
    summary='Editar um proprietário pelo id.',
    status_code=status.HTTP_200_OK,
    response_model=ProprietarioOut,
)
async def edite_proprietario(id:str, db_session: DatabaseDependency, proprietario_up: ProprietarioUpdate):
    return await patch_proprietario(id, db_session, proprietario_up)


@router.delete(
    '/{id}',
    summary='Deletar um proprietário pelo id.',
    status_code=status.HTTP_204_NO_CONTENT
)
async def deletar_proprietario(id:str, db_session: DatabaseDependency):
    return await delete_proprietario(id, db_session)
