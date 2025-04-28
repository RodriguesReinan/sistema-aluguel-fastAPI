import datetime
from uuid import uuid4
from fastapi import status, Body, HTTPException
from api.routes.usuarios.models.usuario_model import UsuarioModel
from api.contrib.tenancy import filter_by_tenant
from api.routes.imoveis.models import ImovelModel
from api.routes.proprietarios.models import ProprietarioModel
from api.routes.imoveis.schemas import ImovelIn, ImovelOut, ImovelUpdate
from sqlalchemy.future import select
from api.contrib.dependecies import DatabaseDependency
from api.services.log_service import registrar_log


async def create_imovel(
        db_session: DatabaseDependency,
        current_user: UsuarioModel,
        imovel_in: ImovelIn = Body(...)
        ) -> ImovelOut:

    proprietario_cpf = imovel_in.proprietario.cpf

    # proprietario = (await db_session.execute(
    #     select(ProprietarioModel).filter(
    #         ProprietarioModel.cpf == proprietario_cpf,
    #         ProprietarioModel.ativo == 1
    #     )
    # )).scalars().first()

    statement = select(ProprietarioModel).filter(ProprietarioModel.cpf == proprietario_cpf,
                                                 ProprietarioModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)

    proprietario = (await db_session.execute(statement)).scalars().first()

    if not proprietario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'O proprietário {proprietario} não foi encontrado'
        )

    try:
        imovel_out = ImovelOut(id=str(uuid4()), **imovel_in.model_dump())
        imovel_model = ImovelModel(**imovel_out.model_dump(exclude={'proprietario'}), tenant_id=current_user.id)

        imovel_model.proprietario_id = proprietario.pk_id

        # verifica se estamos recebendo strings vazias, do frontend
        for key, value in imovel_out.model_dump().items():
            if value is None or (isinstance(value, str) and value.strip() == ""):
                raise HTTPException(status_code=400, detail=f"Campo {key} não pode ser vazio.")

        db_session.add(imovel_model)
        await db_session.commit()
        await db_session.refresh(imovel_model)
        await registrar_log(db_session, "Criação", f"Criou o imóvel: {imovel_model.id}", current_user)

    except Exception as e:
        error_message = str(e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ocorreu um erro ao inserir os dados no banco. Erro: {error_message}'
        )

    return imovel_out


async def get_all_imoveis(db_session: DatabaseDependency, current_user: UsuarioModel) -> list[ImovelOut]:

    # imoveis: list[ImovelOut] = (await db_session.execute(
    #     select(ImovelModel).filter(
    #         ImovelModel.ativo == 1
    #     )
    # )).scalars().all()

    statement = select(ImovelModel).filter(ImovelModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)

    imoveis = (await db_session.execute(statement)).scalars().all()

    return imoveis


async def get_imovel(id: str, db_session: DatabaseDependency, current_user: UsuarioModel) -> ImovelOut:

    # imovel: ImovelOut = (await db_session.execute(
    #     select(ImovelModel).filter(
    #         ImovelModel.id == id,
    #         ImovelModel.ativo == 1
    #     )
    # )).scalars().first()

    statement = select(ImovelModel).filter(ImovelModel.id == id, ImovelModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)

    imovel = (await db_session.execute(statement)).scalars().first()

    if not imovel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Imóvel não encontrado no id {id}'
        )

    return imovel


async def patch_imovel(
        id:str,
        db_session: DatabaseDependency,
        imovel_up: ImovelUpdate, current_user: UsuarioModel
) -> ImovelOut:

    # imovel: ImovelOut = (await db_session.execute(
    #     select(ImovelModel).filter(
    #         ImovelModel.id == id,
    #         ImovelModel.ativo == 1
    #     )
    # )).scalars().first()

    statement = select(ImovelModel).filter(ImovelModel.id == id, ImovelModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)

    imovel = (await db_session.execute(statement)).scalars().first()

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
    await registrar_log(db_session, "Atualização", f"Atualizou o imovel {imovel.id}", current_user)

    return imovel


async def delete_imovel(id: str, db_session: DatabaseDependency, current_user: UsuarioModel) -> None:

    # imovel: ImovelOut = (await db_session.execute(
    #         select(ImovelModel).filter(
    #             ImovelModel.id == id,
    #             ImovelModel.ativo == 1
    #         )
    # )).scalars().first()

    statement = select(ImovelModel).filter(ImovelModel.id == id, ImovelModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)

    imovel = (await db_session.execute(statement)).scalars().first()

    if not imovel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Imóvel não encontrado no id: {id}'
        )

    # await db_session.delete(imovel)
    imovel.deleted_at = datetime.datetime.utcnow()
    imovel.ativo = 0

    await db_session.commit()
    await registrar_log(db_session, "Exclusão", f"Excluiu o imóvel: {imovel.id}", current_user)
