import datetime
from uuid import uuid4
from fastapi import status, Body, HTTPException

from api.routes.contratos.schemas import ContratoIn, ContratoOut, ContratoUpdate

from sqlalchemy.future import select
from api.contrib.dependecies import DatabaseDependency
from api.routes.pagamento.pagamentos_contratos import criar_pagamentos_para_contratos

from api.routes.inquilinos.models import InquilinoModel
from api.routes.imoveis.models import ImovelModel
from api.routes.contratos.models import ContratoModel
from api.routes.usuarios.models.usuario_model import UsuarioModel


async def create_contrato(
        db_session: DatabaseDependency,
        contrato_in: ContratoIn = Body(...),
        ) -> ContratoOut:

    usuario_id = contrato_in.usuario.id

    # usuario = (await db_session.execute(
    #     select(UsuarioModel).filter_by(id=usuario_id)
    # )).scalars().first()

    usuario = (await db_session.execute(
        select(UsuarioModel).filter(
            UsuarioModel.id == usuario_id,
            UsuarioModel.ativo == 1
        )
    )).scalars().first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'O usuário {usuario_id} não foi encontrado'
        )

    inquilino_cpf = contrato_in.inquilino.cpf
    # inquilino = (await db_session.execute(
    #     select(InquilinoModel).filter_by(cpf=inquilino_cpf)
    # )).scalars().first()

    inquilino = (await db_session.execute(
        select(InquilinoModel).filter(
            InquilinoModel.cpf == inquilino_cpf,
            InquilinoModel.ativo == 1
        )
    )).scalars().first()

    if not inquilino:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'O inquilino {inquilino} não foi encontrado'
        )

    imovel_id = contrato_in.imovel.id
    # imovel = (await db_session.execute(
    #     select(ImovelModel).filter_by(id=imovel_id)
    # )).scalars().first()

    imovel = (await db_session.execute(
        select(ImovelModel).filter(
            ImovelModel.id == imovel_id,
            ImovelModel.ativo == 1
        )
    )).scalars().first()

    if not imovel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Imóvel {imovel} não encontrado.'
        )

    try:
        contrato_out = ContratoOut(id=str(uuid4()), **contrato_in.model_dump())

        contrato_model = ContratoModel(**contrato_out.model_dump(exclude={'inquilino', 'imovel', 'usuario'}))

        contrato_model.inquilino_id = inquilino.pk_id
        contrato_model.imovel_id = imovel.pk_id
        contrato_model.usuario_id = usuario.pk_id

        db_session.add(contrato_model)
        await db_session.commit()
        await db_session.refresh(contrato_model)

    except Exception as e:
        error_message = str(e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ocorreu um erro ao inserir os dados no banco. Erro: {error_message}'
        )

    # Criar pagamentos automaticamente
    await criar_pagamentos_para_contratos(contrato_model, db_session)

    # return contrato_out
    # Retornar contrato formatado com imovel formatado
    return ContratoOut.from_model(contrato_model, inquilino, imovel, usuario)

# primeira versão que estava funcionado, antes de eu querer separar numero e bairro do endereço do imóvel
# async def get_all_alugueis(db_session: DatabaseDependency) -> list[ContratoOut]:
#     alugueis: list[ContratoOut] = (await db_session.execute(
#         select(ContratoModel)
#     )).scalars().all()
#
#     return alugueis


async def get_all_alugueis(db_session: DatabaseDependency) -> list[ContratoOut]:
    # result = await db_session.execute(
    #     select(ContratoModel, InquilinoModel, ImovelModel, UsuarioModel)
    #     .join(InquilinoModel, ContratoModel.inquilino_id == InquilinoModel.pk_id)
    #     .join(ImovelModel, ContratoModel.imovel_id == ImovelModel.pk_id)
    #     .join(UsuarioModel, ContratoModel.usuario_id == UsuarioModel.pk_id)
    # )

    result = (await db_session.execute(
        select(ContratoModel, InquilinoModel, ImovelModel, UsuarioModel)
        .join(InquilinoModel, ContratoModel.inquilino_id == InquilinoModel.pk_id)
        .join(ImovelModel, ContratoModel.imovel_id == ImovelModel.pk_id)
        .join(UsuarioModel, ContratoModel.usuario_id == UsuarioModel.pk_id)
        .filter(
            ContratoModel.ativo == 1,
            InquilinoModel.ativo == 1,
            ImovelModel.ativo == 1,
            UsuarioModel.ativo == 1
        )
        ))

    contratos = []
    for contrato_model, inquilino, imovel, usuario in result.all():
        contrato_out = ContratoOut.from_model(contrato_model, inquilino, imovel, usuario)
        contratos.append(contrato_out)

    return contratos


async def get_aluguel(id: str, db_session: DatabaseDependency) -> ContratoOut:
    # aluguel: ContratoOut = (await db_session.execute(
    #     select(ContratoModel).filter_by(id=id)
    # )).scalars().first()

    aluguel: ContratoOut = (await db_session.execute(
        select(ContratoModel).filter(
            ContratoModel.id == id,
            ContratoModel.ativo == 1
        )
    )).scalars().first()

    if not aluguel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Contrato de aluguel não encontrado no id {id}'
        )
    return aluguel


async def patch_aluguel(id: str, db_session: DatabaseDependency, aluguel_up: ContratoUpdate) -> ContratoOut:
    # aluguel: ContratoOut = (await db_session.execute(
    #     select(ContratoModel).filter_by(id=id)
    # )).scalars().first()

    aluguel: ContratoOut = (await db_session.execute(
        select(ContratoModel).filter(
            ContratoModel.id == id,
            ContratoModel.ativo == 1
        )
    )).scalars().first()

    if not aluguel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Contrato de aluguel não encontrado no id {id}'
        )

    aluguel_update = aluguel_up.model_dump(exclude_unset=True)
    for key, value in aluguel_update.items():
        setattr(aluguel, key, value)

    await db_session.commit()
    await db_session.refresh(aluguel)

    return aluguel


async def delete_aluguel(id: str, db_session: DatabaseDependency) -> None:
    # aluguel: ContratoOut = (await db_session.execute(
    #     select(ContratoModel).filter_by(id=id)
    # )).scalars().first()

    aluguel: ContratoOut = (await db_session.execute(
        select(ContratoModel).filter(
            ContratoModel.id == id,
            ContratoModel.ativo == 1
        )
    )).scalars().first()

    if not aluguel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Contrato de aluguel não encontrado no id {id}'
        )

    # await db_session.delete(aluguel)
    aluguel.deleted_at = datetime.datetime.utcnow()
    aluguel.ativo = 0

    await db_session.commit()
