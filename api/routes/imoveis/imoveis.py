from fastapi import APIRouter, status
from api.routes.imoveis.schemas import ImovelIn, ImovelOut, ImovelUpdate
from api.services.imovel_service import (create_imovel, get_all_imoveis, get_imovel, patch_imovel, delete_imovel)
from api.contrib.dependecies import DatabaseDependency


router = APIRouter()


@router.post(
    "/",
    summary='Criar um novo imóvel',
    status_code=status.HTTP_201_CREATED,
    response_model=ImovelOut
)
async def criar_imovel(imovel: ImovelIn, db_session: DatabaseDependency):
    return await create_imovel(db_session, imovel)


@router.get(
    path='/',
    summary='Consultar todos os imóveis',
    status_code=status.HTTP_200_OK,
    response_model=list[ImovelOut],
)
async def listar_imoveis(db_session: DatabaseDependency):
    return await get_all_imoveis(db_session)


@router.get(
    path='/{id}',
    summary='Consultar um imovel',
    status_code=status.HTTP_200_OK,
    response_model=ImovelOut,
)
async def listar_imovel_id(id:str, db_session: DatabaseDependency):
    return await get_imovel(id, db_session)


@router.patch(
    '/{id}',
    summary='Editar um imóvel pelo id.',
    status_code=status.HTTP_200_OK,
    response_model=ImovelOut,
)
async def edite_imovel(id:str, db_session: DatabaseDependency, imovel_up: ImovelUpdate):
    return await patch_imovel(id, db_session, imovel_up)


@router.delete(
    '/{id}',
    summary='Deletar um imóvel pelo id.',
    status_code=status.HTTP_204_NO_CONTENT
)
async def deletar_imovel(id:str, db_session: DatabaseDependency):
    return await delete_imovel(id, db_session)
