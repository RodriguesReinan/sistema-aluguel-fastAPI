from fastapi import APIRouter, status, Depends
from api.routes.contratos.schemas import ContratoIn, ContratoOut, ContratoUpdate
from api.services.contrato_service import (create_contrato, get_all_alugueis, get_aluguel, patch_aluguel,
                                           delete_aluguel)
from api.contrib.dependecies import DatabaseDependency
from api.routes.usuarios.dependecies import get_current_user
from api.routes.usuarios.models.usuario_model import UsuarioModel


router = APIRouter()


@router.post(
    "/",
    summary='Criar um novo contratos',
    status_code=status.HTTP_201_CREATED,
    response_model=ContratoOut
)
async def criar_contrato(contrato: ContratoIn, db_session: DatabaseDependency,
                         current_user: UsuarioModel = Depends(get_current_user)):
    return await create_contrato(db_session, current_user, contrato)


@router.get(
    '/',
    summary='Consultar todos os contratos de aluguel',
    status_code=status.HTTP_200_OK,
    response_model=list[ContratoOut]
)
async def listar_alugueis(db_session: DatabaseDependency, current_user: UsuarioModel = Depends(get_current_user)):
    return await get_all_alugueis(db_session, current_user)


@router.get(
    path='/{id}',
    summary='Consultar um contrato',
    status_code=status.HTTP_200_OK,
    response_model=ContratoOut,
)
async def listar_aluguel_id(id: str, db_session: DatabaseDependency, current_user: UsuarioModel = Depends(get_current_user)):
    return await get_aluguel(id, db_session, current_user)


@router.patch(
    '/{id}',
    summary='Editar um aluguel pelo id.',
    status_code=status.HTTP_200_OK,
    response_model=ContratoOut,
)
async def edite_aluguel(id: str, db_session: DatabaseDependency, alugel_up: ContratoUpdate,
                        current_user: UsuarioModel = Depends(get_current_user)):
    return await patch_aluguel(id, db_session, alugel_up, current_user)


@router.delete(
    '/{id}',
    summary='Deletar um aluguel pelo id.',
    status_code=status.HTTP_204_NO_CONTENT
)
async def deletar_aluguel(id:str, db_session: DatabaseDependency, current_user: UsuarioModel = Depends(get_current_user)):
    return await delete_aluguel(id, db_session, current_user)
