from uuid import uuid4
import re
from fastapi import status, Body, HTTPException
from sqlalchemy.exc import IntegrityError
from api.routes.inquilinos.models import InquilinoModel
from api.routes.inquilinos.schemas import InquilinoIn, InquilinoOut, InquilinoUpdate
from sqlalchemy.future import select
from api.contrib.dependecies import DatabaseDependency
import datetime


async def create_inquilino(db_session: DatabaseDependency, inquilino_in: InquilinoIn = Body(...)) -> InquilinoOut:

    try:
        inquilino_out = InquilinoOut(id=str(uuid4()), **inquilino_in.model_dump())
        inquilino_model = InquilinoModel(**inquilino_out.model_dump())

        db_session.add(inquilino_model)
        await db_session.commit()
        await db_session.refresh(inquilino_model)

    except IntegrityError as e:
        error_message = str(e)

        # Expressão regular para capturar "Duplicate entry '99999999999'"
        match = re.search(r"Duplicate entry '([^']+)", error_message)

        if match:
            duplicate_entry = match.group(1)  # Captura a string completa: "Duplicate entry '99999999999'"
            duplicate_entry = f"CPF já cadastrado: {duplicate_entry}"
        else:
            duplicate_entry = "Erro de integridade desconhecido"

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ocorreu um erro ao inserir os dados no banco. Erro: {duplicate_entry}'
        )

    return inquilino_out


async def get_all_inquilinos(db_session: DatabaseDependency) -> list[InquilinoOut]:
    # inquilinos: list[InquilinoOut] = (await db_session.execute(select(InquilinoModel))).scalars().all()

    inquilinos: list[InquilinoOut] = (await db_session.execute(
        select(InquilinoModel).filter(InquilinoModel.ativo == 1)
    )).scalars().all()

    return inquilinos


async def get_inquilino(id: str, db_session: DatabaseDependency) -> InquilinoOut:
    # inquilino: InquilinoOut = (await db_session.execute(select(InquilinoModel).filter_by(id=id))
    #                                  ).scalars().first()

    inquilino: InquilinoOut = (await db_session.execute(
        select(InquilinoModel).filter(
            InquilinoModel.id == id,
            InquilinoModel.ativo == 1
        )
    )).scalars().first()

    if not inquilino:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Inquilino não encontrado no id {id}'
        )

    return inquilino


async def patch_inquilino(id:str, db_session: DatabaseDependency, inquilino_up: InquilinoUpdate) -> InquilinoOut:

    # inquilino: InquilinoOut = (await db_session.execute(select(InquilinoModel).filter_by(id=id))
    #                            ).scalars().first()

    inquilino: InquilinoOut = (await db_session.execute(
        select(InquilinoModel).filter(
            InquilinoModel.id == id,
            InquilinoModel.ativo == 1
        )
    )).scalars().first()

    if not inquilino:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Inquilino não encontrado no id {id}'
        )
    inquilino_update = inquilino_up.model_dump(exclude_unset=True)
    for key, value in inquilino_update.items():
        setattr(inquilino, key, value)

    await db_session.commit()
    await db_session.refresh(inquilino)

    return inquilino


async def delete_inquilino(id: str, db_session: DatabaseDependency) -> None:
    # inquilino: InquilinoOut = (
    #     await db_session.execute(select(InquilinoModel).filter_by(id=id))
    # ).scalars().first()

    inquilino: InquilinoOut = (
        await db_session.execute(
            select(InquilinoModel).filter(
                InquilinoModel.id == id,
                InquilinoModel.ativo == 1
            )
        )).scalars().first()

    if not inquilino:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Inquilino não encontrado no id: {id}'
        )

    # await db_session.delete(inquilino)
    inquilino.deleted_at = datetime.datetime.utcnow()
    inquilino.ativo = 0

    await db_session.commit()
