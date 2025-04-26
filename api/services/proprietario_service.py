import datetime
from uuid import uuid4
import re

from fastapi import status, Body, HTTPException
from sqlalchemy.exc import IntegrityError
from api.routes.proprietarios.models import ProprietarioModel
from api.routes.proprietarios.schemas import ProprietarioIn, ProprietarioOut, ProprietarioUpdate
from sqlalchemy.future import select
from api.contrib.dependecies import DatabaseDependency


async def create_proprietario(
        db_session: DatabaseDependency,
        proprietario_in: ProprietarioIn = Body(...)
        ) -> ProprietarioOut:

    try:
        proprietario_out = ProprietarioOut(id=str(uuid4()), **proprietario_in.model_dump())
        proprietario_model = ProprietarioModel(**proprietario_out.model_dump())

        db_session.add(proprietario_model)
        await db_session.commit()
        await db_session.refresh(proprietario_model)
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


async def get_all_proprietarios(db_session: DatabaseDependency) -> list[ProprietarioOut]:
    # proprietarios: list[ProprietarioOut] = (await db_session.execute(select(ProprietarioModel))).scalars().all()

    proprietarios: list[ProprietarioOut] = (await db_session.execute(
        select(ProprietarioModel).filter(
            ProprietarioModel.ativo == 1
        )
    )).scalars().all()

    return proprietarios


async def get_proprietario(id: str, db_session: DatabaseDependency) -> ProprietarioOut:
    # proprietario: ProprietarioOut = (await db_session.execute(
    #     select(ProprietarioModel).filter_by(id=id)
    # )).scalars().first()

    proprietario: ProprietarioOut = (await db_session.execute(
        select(ProprietarioModel).filter(
            ProprietarioModel.id == id,
            ProprietarioModel.ativo == 1
        )
    )).scalars().first()

    if not proprietario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Proprietário não encontrado no id {id}'
        )

    return proprietario


async def patch_proprietario(
        id:str,
        db_session: DatabaseDependency,
        proprietario_up: ProprietarioUpdate
) -> ProprietarioOut:

    # proprietario: ProprietarioOut = (await db_session.execute(select(ProprietarioModel).filter_by(id=id))
    #                                  ).scalars().first()

    proprietario: ProprietarioOut = (await db_session.execute(
        select(ProprietarioModel).filter(
            ProprietarioModel.id == id,
            ProprietarioModel.ativo == 1
        )
    )).scalars().first()

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

    return proprietario


async def delete_proprietario(id: str, db_session: DatabaseDependency) -> None:
    # proprietario: ProprietarioOut = (
    #     await db_session.execute(select(ProprietarioModel).filter_by(id=id))
    # ).scalars().first()

    proprietario: ProprietarioOut = (await db_session.execute(
        select(ProprietarioModel).filter(
            ProprietarioModel.id == id,
            ProprietarioModel.ativo == 1
        )
    )).scalars().first()

    if not proprietario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Proprietário não encontrado no id: {id}'
        )

    # await db_session.delete(proprietario)
    proprietario.deleted_at = datetime.datetime.utcnow()
    proprietario.ativo = 0

    await db_session.commit()
