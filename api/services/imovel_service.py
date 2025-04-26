import datetime
from uuid import uuid4
import re

from fastapi import status, Body, HTTPException
from sqlalchemy.exc import IntegrityError
from api.routes.imoveis.models import ImovelModel
from api.routes.proprietarios.models import ProprietarioModel
from api.routes.imoveis.schemas import ImovelIn, ImovelOut, ImovelUpdate
from sqlalchemy.future import select
from api.contrib.dependecies import DatabaseDependency


async def create_imovel(
        db_session: DatabaseDependency,
        imovel_in: ImovelIn = Body(...)
        ) -> ImovelOut:

    proprietario_cpf = imovel_in.proprietario.cpf
    # proprietario = (await db_session.execute(
    #     select(ProprietarioModel).filter_by(cpf=proprietario_cpf)
    # )).scalars().first()

    proprietario = (await db_session.execute(
        select(ProprietarioModel).filter(
            ProprietarioModel.cpf == proprietario_cpf,
            ProprietarioModel.ativo == 1
        )
    )).scalars().first()

    if not proprietario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'O proprietário {proprietario} não foi encontrado'
        )

    try:
        imovel_out = ImovelOut(id=str(uuid4()), **imovel_in.model_dump())
        imovel_model = ImovelModel(**imovel_out.model_dump(exclude={'proprietario'}))

        imovel_model.proprietario_id = proprietario.pk_id

        db_session.add(imovel_model)
        await db_session.commit()
        await db_session.refresh(imovel_model)
    except Exception as e:
        error_message = str(e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ocorreu um erro ao inserir os dados no banco. Erro: {error_message}'
        )

    return imovel_out


async def get_all_imoveis(db_session: DatabaseDependency) -> list[ImovelOut]:
    # imoveis: list[ImovelOut] = (await db_session.execute(select(ImovelModel))).scalars().all()

    imoveis: list[ImovelOut] = (await db_session.execute(
        select(ImovelModel).filter(
            ImovelModel.ativo == 1
        )
    )).scalars().all()

    return imoveis


async def get_imovel(id: str, db_session: DatabaseDependency) -> ImovelOut:
    # imovel: ImovelOut = (await db_session.execute(select(ImovelModel).filter_by(id=id))).scalars().first()

    imovel: ImovelOut = (await db_session.execute(
        select(ImovelModel).filter(
            ImovelModel.id == id,
            ImovelModel.ativo == 1
        )
    )).scalars().first()

    if not imovel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Imóvel não encontrado no id {id}'
        )

    return imovel


async def patch_imovel(
        id:str,
        db_session: DatabaseDependency,
        imovel_up: ImovelUpdate
) -> ImovelOut:

    # imovel: ImovelOut = (await db_session.execute(select(ImovelModel).filter_by(id=id))).scalars().first()

    imovel: ImovelOut = (await db_session.execute(
        select(ImovelModel).filter(
            ImovelModel.id == id,
            ImovelModel.ativo == 1
        )
    )).scalars().first()

    if not imovel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Imóvel não encontrado no id {id}'
        )
    imovel_update = imovel_up.model_dump(exclude_unset=True)
    for key, value in imovel_update.items():
        setattr(imovel, key, value)

    await db_session.commit()
    await db_session.refresh(imovel)

    return imovel


async def delete_imovel(id: str, db_session: DatabaseDependency) -> None:
    # imovel: ImovelOut = (
    #     await db_session.execute(select(ImovelModel).filter_by(id=id))
    # ).scalars().first()

    imovel: ImovelOut = (await db_session.execute(
            select(ImovelModel).filter(
                ImovelModel.id == id,
                ImovelModel.ativo == 1
            )
    )).scalars().first()

    if not imovel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Imóvel não encontrado no id: {id}'
        )

    # await db_session.delete(imovel)
    imovel.deleted_at = datetime.datetime.utcnow()
    imovel.ativo = 0

    await db_session.commit()
