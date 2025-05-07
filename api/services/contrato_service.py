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
from api.services.log_service import registrar_log
from api.contrib.tenancy import filter_by_tenant


async def create_contrato(
        db_session: DatabaseDependency,
        current_user: UsuarioModel,
        contrato_in: ContratoIn = Body(...),
        ) -> ContratoOut:

    usuario_id = contrato_in.usuario.id

    # usuario = (await db_session.execute(
    #     select(UsuarioModel).filter(
    #         UsuarioModel.id == usuario_id,
    #         UsuarioModel.ativo == 1
    #     )
    # )).scalars().first()

    statement = select(UsuarioModel).filter(UsuarioModel.id == usuario_id, UsuarioModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)
    usuario = (await db_session.execute(statement)).scalars().first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'O usuário {usuario_id} não foi encontrado'
        )

    inquilino_cpf = contrato_in.inquilino.cpf

    # inquilino = (await db_session.execute(
    #     select(InquilinoModel).filter(
    #         InquilinoModel.cpf == inquilino_cpf,
    #         InquilinoModel.ativo == 1
    #     )
    # )).scalars().first()

    statement = select(InquilinoModel).filter(InquilinoModel.cpf == inquilino_cpf, InquilinoModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)
    inquilino = (await db_session.execute(statement)).scalars().first()

    if not inquilino:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'O inquilino {inquilino} não foi encontrado'
        )

    imovel_id = contrato_in.imovel.id

    # imovel = (await db_session.execute(
    #     select(ImovelModel).filter(
    #         ImovelModel.id == imovel_id,
    #         ImovelModel.ativo == 1
    #     )
    # )).scalars().first()

    statement = select(ImovelModel).filter(ImovelModel.id == imovel_id, ImovelModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)
    imovel = (await db_session.execute(statement)).scalars().first()

    if not imovel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Imóvel {imovel} não encontrado.'
        )

    # substiui a partir daqui...................
    # Começa a transação manualmente

    try:
        # Verifica se já existe uma transação ativa
        if db_session.in_transaction():
            # Se já está em uma transação, usa a sessão existente
            contrato_out = ContratoOut(id=str(uuid4()), **contrato_in.model_dump())
            contrato_model = ContratoModel(
                **contrato_out.model_dump(exclude={'inquilino', 'imovel', 'usuario'}),
                tenant_id=current_user.id
            )

            contrato_model.inquilino_id = inquilino.pk_id
            contrato_model.imovel_id = imovel.pk_id
            contrato_model.usuario_id = usuario.pk_id

            # verifica se estamos recebendo strings vazias, do frontend
            # for key, value in contrato_out.model_dump().items():
            #     if value is None or (isinstance(value, str) and value.strip() == ""):
            #         raise HTTPException(status_code=400, detail=f"Campo {key} não pode ser vazio.")

            db_session.add(contrato_model)
            await db_session.flush()  # Persiste o contrato sem commit
            await db_session.refresh(contrato_model)

            # Cria os pagamentos
            await criar_pagamentos_para_contratos(contrato_model, db_session, current_user)

            await db_session.commit()

            await registrar_log(db_session, "Criação", f"Criou o contrato: {contrato_model.id}", current_user)
        else:
            # Se não há transação ativa, inicia uma nova
            async with db_session.begin():
                contrato_out = ContratoOut(id=str(uuid4()), **contrato_in.model_dump())
                contrato_model = ContratoModel(
                    **contrato_out.model_dump(exclude={'inquilino', 'imovel', 'usuario'}),
                    tenant_id=current_user.id
                )

                contrato_model.inquilino_id = inquilino.pk_id
                contrato_model.imovel_id = imovel.pk_id
                contrato_model.usuario_id = usuario.pk_id

                db_session.add(contrato_model)
                await db_session.flush()  # Persiste o contrato sem commit
                await db_session.refresh(contrato_model)

                # Cria os pagamentos
                await criar_pagamentos_para_contratos(contrato_model, db_session, current_user)

        return ContratoOut.from_model(contrato_model, inquilino, imovel, usuario)

    except Exception as e:
        # Garante rollback se a transação foi iniciada localmente ou lança o erro
        if not db_session.in_transaction():
            await db_session.rollback()
        error_message = str(e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ocorreu um erro ao processar a transação. Erro: {error_message}'
        )

    # try:
    #     contrato_out = ContratoOut(id=str(uuid4()), **contrato_in.model_dump())
    #
    #     contrato_model = ContratoModel(**contrato_out.model_dump(exclude={'inquilino', 'imovel', 'usuario'}),
    #                                    tenant_id=current_user.id)
    #
    #     contrato_model.inquilino_id = inquilino.pk_id
    #     contrato_model.imovel_id = imovel.pk_id
    #     contrato_model.usuario_id = usuario.pk_id
    #
    #     db_session.add(contrato_model)
    #     await db_session.commit()
    #     await db_session.refresh(contrato_model)
    #
    # except Exception as e:
    #     error_message = str(e)
    #
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=f'Ocorreu um erro ao inserir os dados no banco. Erro: {error_message}'
    #     )
    #
    # # Criar pagamentos automaticamente
    # await criar_pagamentos_para_contratos(contrato_model, db_session, current_user)
    #
    # # return contrato_out
    # # Retornar contrato formatado com imovel formatado
    # return ContratoOut.from_model(contrato_model, inquilino, imovel, usuario)


async def get_all_alugueis(db_session: DatabaseDependency, current_user: UsuarioModel) -> list[ContratoOut]:

    # result = (await db_session.execute(
    #     select(ContratoModel, InquilinoModel, ImovelModel, UsuarioModel)
    #     .join(InquilinoModel, ContratoModel.inquilino_id == InquilinoModel.pk_id)
    #     .join(ImovelModel, ContratoModel.imovel_id == ImovelModel.pk_id)
    #     .join(UsuarioModel, ContratoModel.usuario_id == UsuarioModel.pk_id)
    #     .filter(
    #         ContratoModel.ativo == 1,
    #         InquilinoModel.ativo == 1,
    #         ImovelModel.ativo == 1,
    #         UsuarioModel.ativo == 1
    #     )
    #     ))

    statement = (select(ContratoModel, InquilinoModel, ImovelModel, UsuarioModel).join(
        InquilinoModel, ContratoModel.inquilino_id == InquilinoModel.pk_id).join(
        ImovelModel, ContratoModel.imovel_id == ImovelModel.pk_id).join(
        UsuarioModel, ContratoModel.usuario_id == UsuarioModel.pk_id)
        .filter(
            ContratoModel.ativo == 1,
            InquilinoModel.ativo == 1,
            ImovelModel.ativo == 1,
            UsuarioModel.ativo == 1
        )
    )

    statement = filter_by_tenant(statement, current_user.id)

    result = (await db_session.execute(statement))

    contratos = []
    for contrato_model, inquilino, imovel, usuario in result.all():
        contrato_out = ContratoOut.from_model(contrato_model, inquilino, imovel, usuario)
        contratos.append(contrato_out)

    return contratos


async def get_aluguel(id: str, db_session: DatabaseDependency, current_user: UsuarioModel) -> ContratoOut:

    # aluguel: ContratoOut = (await db_session.execute(
    #     select(ContratoModel).filter(
    #         ContratoModel.id == id,
    #         ContratoModel.ativo == 1
    #     )
    # )).scalars().first()

    statement = select(ContratoModel).filter(ContratoModel.id == id, ContratoModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)

    aluguel = (await db_session.execute(statement)).scalars().first()

    if not aluguel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Contrato de aluguel não encontrado no id {id}'
        )
    return aluguel


async def patch_aluguel(id: str, db_session: DatabaseDependency, aluguel_up: ContratoUpdate,
                        current_user: UsuarioModel) -> ContratoOut:

    # aluguel: ContratoOut = (await db_session.execute(
    #     select(ContratoModel).filter(
    #         ContratoModel.id == id,
    #         ContratoModel.ativo == 1
    #     )
    # )).scalars().first()

    statement = select(ContratoModel).filter(ContratoModel.id == id, ContratoModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)

    aluguel = (await db_session.execute(statement)).scalars().first()

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

    await registrar_log(db_session, "Atualização", f"Atualizou o contrato: {aluguel.id}", current_user)

    return aluguel


async def delete_aluguel(id: str, db_session: DatabaseDependency, current_user: UsuarioModel) -> None:

    # aluguel: ContratoOut = (await db_session.execute(
    #     select(ContratoModel).filter(
    #         ContratoModel.id == id,
    #         ContratoModel.ativo == 1
    #     )
    # )).scalars().first()

    statement = select(ContratoModel).filter(ContratoModel.id == id, ContratoModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)

    aluguel = (await db_session.execute(statement)).scalars().first()

    if not aluguel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Contrato de aluguel não encontrado no id {id}'
        )

    # await db_session.delete(aluguel)
    aluguel.deleted_at = datetime.datetime.utcnow()
    aluguel.ativo = 0

    await db_session.commit()

    await registrar_log(db_session, "Exclusão", f"Excluiu o aluguel {aluguel.id}", current_user)
