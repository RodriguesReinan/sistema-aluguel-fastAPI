from fastapi import APIRouter, status, Depends
from api.routes.imoveis.schemas import ImovelIn, ImovelOut, ImovelUpdate
from api.services.imovel_service import (create_imovel, get_all_imoveis, get_imovel, patch_imovel, delete_imovel)
from api.contrib.dependecies import DatabaseDependency
from api.routes.usuarios.dependecies import get_current_user
from api.routes.usuarios.models.usuario_model import UsuarioModel


router = APIRouter()


@router.post(
    "/",
    summary='Criar um novo imóvel',
    status_code=status.HTTP_201_CREATED,
    response_model=ImovelOut
)
async def criar_imovel(imovel: ImovelIn, db_session: DatabaseDependency,
                       current_user: UsuarioModel = Depends(get_current_user)):
    return await create_imovel(db_session, current_user, imovel)


@router.get(
    path='/',
    summary='Consultar todos os imóveis',
    status_code=status.HTTP_200_OK,
    response_model=list[ImovelOut],
)
async def listar_imoveis(db_session: DatabaseDependency, current_user: UsuarioModel = Depends(get_current_user)):
    return await get_all_imoveis(db_session, current_user)


@router.get(
    path='/{id}',
    summary='Consultar um imovel',
    status_code=status.HTTP_200_OK,
    response_model=ImovelOut,
)
async def listar_imovel_id(id:str, db_session: DatabaseDependency,
                           current_user: UsuarioModel = Depends(get_current_user)):
    return await get_imovel(id, db_session, current_user)


@router.patch(
    '/{id}',
    summary='Editar um imóvel pelo id.',
    status_code=status.HTTP_200_OK,
    response_model=ImovelOut,
)
async def editar_imovel(id:str, db_session: DatabaseDependency, imovel_up: ImovelUpdate,
                        current_user: UsuarioModel = Depends(get_current_user)):
    return await patch_imovel(id, db_session, imovel_up, current_user)


@router.delete(
    '/{id}',
    summary='Deletar um imóvel pelo id.',
    status_code=status.HTTP_204_NO_CONTENT
)
async def deletar_imovel(id:str, db_session: DatabaseDependency,
                         current_user: UsuarioModel = Depends(get_current_user)):
    return await delete_imovel(id, db_session, current_user)
