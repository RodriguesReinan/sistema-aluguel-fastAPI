from uuid import uuid4
import re
from fastapi import status, Body, HTTPException
from sqlalchemy.exc import IntegrityError
from api.routes.inquilinos.models import InquilinoModel
from api.routes.inquilinos.schemas import InquilinoIn, InquilinoOut, InquilinoUpdate
from sqlalchemy.future import select
from api.contrib.dependecies import DatabaseDependency
from api.routes.usuarios.models.usuario_model import UsuarioModel
from api.contrib.tenancy import filter_by_tenant
from api.services.log_service import registrar_log
import datetime


async def create_inquilino(
        db_session: DatabaseDependency,
        current_user: UsuarioModel,
        inquilino_in: InquilinoIn = Body(...)
) -> InquilinoOut:

    try:
        inquilino_out = InquilinoOut(id=str(uuid4()), **inquilino_in.model_dump())
        inquilino_model = InquilinoModel(**inquilino_out.model_dump(), tenant_id=current_user.id)

        # verifica se estamos recebendo strings vazias, do frontend
        for key, value in inquilino_out.model_dump().items():
            if value is None or (isinstance(value, str) and value.strip() == ""):
                raise HTTPException(status_code=400, detail=f"Campo {key} não pode ser vazio.")

        db_session.add(inquilino_model)
        await db_session.commit()
        await db_session.refresh(inquilino_model)
        await registrar_log(db_session, "Criação", f"Criou o inquilino {inquilino_model.nome}", current_user)

        return inquilino_out

    except IntegrityError as e:
        error_message = str(e)

        # Expressão regular para capturar "Duplicate entry '99999999999'"
        match = re.search(r"Duplicate entry '([^']+)", error_message)

        if match:
            duplicate_value = match.group(1)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'O valor {duplicate_value} já está cadastrado.'
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro de integridade ao inserir os dados. Tente novamente mais tarde."
        )

    except Exception:
        # Captura qualquer outra falha inesperada
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro inesperado ao criar o inquilino. Por favor, tente novamente."
        )

        # if match:
        #     duplicate_entry = match.group(1)  # Captura a string completa: "Duplicate entry '99999999999'"
        #     duplicate_entry = f"CPF já cadastrado: {duplicate_entry}"
        # else:
        #     duplicate_entry = "Erro de integridade desconhecido"
        #
        # raise HTTPException(
        #     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #     detail=f'Ocorreu um erro ao inserir os dados no banco. Tente novamente mais tarde'
        # )

    # return inquilino_out


async def get_all_inquilinos(db_session: DatabaseDependency, current_user: UsuarioModel) -> list[InquilinoOut]:

    # inquilinos: list[InquilinoOut] = (await db_session.execute(
    #     select(InquilinoModel).filter(
    #         InquilinoModel.ativo == 1,
    #         InquilinoModel.tenant_id == current_user.id
    #     )
    # )).scalars().all()

    statement = select(InquilinoModel).filter(InquilinoModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)

    inquilinos = (await db_session.execute(statement)).scalars().all()

    return inquilinos


async def get_inquilino(id: str, db_session: DatabaseDependency, current_user: UsuarioModel) -> InquilinoOut:

    # inquilino: InquilinoOut = (await db_session.execute(
    #     select(InquilinoModel).filter(
    #         InquilinoModel.id == id,
    #         InquilinoModel.ativo == 1
    #     )
    # )).scalars().first()

    statement = select(InquilinoModel).filter(InquilinoModel.id == id, InquilinoModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)

    inquilino = (await db_session.execute(statement)).scalars().first()

    if not inquilino:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Inquilino não encontrado no id {id}'
        )

    return inquilino


async def patch_inquilino(
        id: str, db_session: DatabaseDependency,
        inquilino_up: InquilinoUpdate,
        current_user: UsuarioModel
        ) -> InquilinoOut:

    # inquilino: InquilinoOut = (await db_session.execute(
    #     select(InquilinoModel).filter(
    #         InquilinoModel.id == id,
    #         InquilinoModel.ativo == 1
    #     )
    # )).scalars().first()

    statement = select(InquilinoModel).filter(InquilinoModel.id == id, InquilinoModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)

    inquilino = (await db_session.execute(statement)).scalars().first()

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
    await registrar_log(db_session, "Atualização", f"Atualizou o inquilino {inquilino.nome}", current_user)

    return inquilino


async def delete_inquilino(id: str, db_session: DatabaseDependency, current_user: UsuarioModel) -> None:

    # inquilino: InquilinoOut = (
    #     await db_session.execute(
    #         select(InquilinoModel).filter(
    #             InquilinoModel.id == id,
    #             InquilinoModel.ativo == 1
    #         )
    #     )).scalars().first()

    statement = select(InquilinoModel).filter(InquilinoModel.id == id, InquilinoModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)

    inquilino = (await db_session.execute(statement)).scalars().first()

    if not inquilino:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Inquilino não encontrado no id: {id}'
        )

    # await db_session.delete(inquilino)
    inquilino.deleted_at = datetime.datetime.utcnow()
    inquilino.ativo = 0

    await db_session.commit()
    await registrar_log(db_session, "Exclusão", f"Excluiu o inquilino {inquilino.nome}", current_user)
