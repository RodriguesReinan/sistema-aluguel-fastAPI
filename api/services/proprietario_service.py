import datetime
from uuid import uuid4
import re

from fastapi import status, Body, HTTPException
from sqlalchemy.exc import IntegrityError
from api.routes.proprietarios.models import ProprietarioModel
from api.routes.proprietarios.schemas import ProprietarioIn, ProprietarioOut, ProprietarioUpdate
from sqlalchemy.future import select
from api.contrib.dependecies import DatabaseDependency
from api.routes.usuarios.models.usuario_model import UsuarioModel
from api.contrib.tenancy import filter_by_tenant
from api.services.log_service import registrar_log


async def create_proprietario(
        db_session: DatabaseDependency,
        current_user: UsuarioModel,
        proprietario_in: ProprietarioIn = Body(...)
        ) -> ProprietarioOut:

    try:
        proprietario_out = ProprietarioOut(id=str(uuid4()), **proprietario_in.model_dump())
        proprietario_model = ProprietarioModel(**proprietario_out.model_dump(), tenant_id=current_user.id)

        # # verifica se estamos recebendo strings vazias, do frontend
        # for key, value in proprietario_out.model_dump().items():
        #     if value is None or (isinstance(value, str) and value.strip() == ""):
        #         raise HTTPException(status_code=400, detail=f"Campo {key} não pode ser vazio.")

        db_session.add(proprietario_model)
        await db_session.commit()
        await db_session.refresh(proprietario_model)
        await registrar_log(db_session, "Criação", f"Criou o proprietário: {proprietario_model.nome}", current_user)

    except IntegrityError as e:
        error_message = str(e)

        # Expressão regular para capturar "Duplicate entry '99999999999'"
        match = re.search(r"Duplicate entry '([^']+)' for key 'proprietarios.cpf'", error_message)
        if match:
            duplicate_entry = match.group(1)  # Captura a string completa: "Duplicate entry '99999999999'"
            duplicate_entry = f"CPF já cadastrado: {duplicate_entry}"
        else:
            duplicate_entry = "Erro de integridade desconhecido"

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ocorreu um erro ao inserir os dados no banco. Erro: {duplicate_entry}'
        )

    return proprietario_out


async def get_all_proprietarios(db_session: DatabaseDependency, current_user: UsuarioModel) -> list[ProprietarioOut]:

    # proprietarios: list[ProprietarioOut] = (await db_session.execute(
    #     select(ProprietarioModel).filter(
    #         ProprietarioModel.ativo == 1
    #     )
    # )).scalars().all()

    statement = select(ProprietarioModel).filter(ProprietarioModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)

    proprietarios = (await db_session.execute(statement)).scalars().all()

    return proprietarios


async def get_proprietario(id: str, db_session: DatabaseDependency, current_user: UsuarioModel) -> ProprietarioOut:

    # proprietario: ProprietarioOut = (await db_session.execute(
    #     select(ProprietarioModel).filter(
    #         ProprietarioModel.id == id,
    #         ProprietarioModel.ativo == 1
    #     )
    # )).scalars().first()

    statement = select(ProprietarioModel).filter(ProprietarioModel.id == id, ProprietarioModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)

    proprietario = (await db_session.execute(statement)).scalars().first()

    if not proprietario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Proprietário não encontrado no id {id}'
        )

    return proprietario


async def patch_proprietario(
        id:str,
        db_session: DatabaseDependency,
        proprietario_up: ProprietarioUpdate,
        current_user: UsuarioModel
) -> ProprietarioOut:

    # proprietario: ProprietarioOut = (await db_session.execute(
    #     select(ProprietarioModel).filter(
    #         ProprietarioModel.id == id,
    #         ProprietarioModel.ativo == 1
    #     )
    # )).scalars().first()

    statement = select(ProprietarioModel).filter(ProprietarioModel.id == id, ProprietarioModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)

    proprietario = (await db_session.execute(statement)).scalars().first()

    if not proprietario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Proprietário não encontrado no id {id}'
        )
    proprietario_update = proprietario_up.model_dump(exclude_unset=True)
    for key, value in proprietario_update.items():
        setattr(proprietario, key, value)

    await db_session.commit()
    await db_session.refresh(proprietario)
    await registrar_log(db_session, "Atualização", f"Atualizou o proprietário: {proprietario.nome}", current_user)

    return proprietario


async def delete_proprietario(id: str, db_session: DatabaseDependency, current_user: UsuarioModel) -> None:

    # proprietario: ProprietarioOut = (await db_session.execute(
    #     select(ProprietarioModel).filter(
    #         ProprietarioModel.id == id,
    #         ProprietarioModel.ativo == 1
    #     )
    # )).scalars().first()

    statement = select(ProprietarioModel).filter(ProprietarioModel.id == id, ProprietarioModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)

    proprietario = (await db_session.execute(statement)).scalars().first()

    if not proprietario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Proprietário não encontrado no id: {id}'
        )

    # await db_session.delete(proprietario)
    proprietario.deleted_at = datetime.datetime.utcnow()
    proprietario.ativo = 0

    await db_session.commit()
    await registrar_log(db_session, "Exclusão", f"Excluiu o proprietário: {proprietario.nome}", current_user)
