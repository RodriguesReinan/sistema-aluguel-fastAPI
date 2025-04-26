from uuid import uuid4
import re
from fastapi import status, Body, HTTPException
from sqlalchemy.exc import IntegrityError
from api.routes.tokens_dispositivos.token_model import TokenDispositivoModel
from api.routes.tokens_dispositivos.schemas import TokenSchameIn, TokenSchemaOut
from api.routes.usuarios.models.usuario_model import UsuarioModel
from api.contrib.dependecies import DatabaseDependency
from sqlalchemy.future import select


async def register_token(db_session: DatabaseDependency, token_data_in: TokenSchameIn = Body(...)) -> TokenSchemaOut:
    try:
        usuario_id = token_data_in.usuario.id
        usuario = (await db_session.execute(
            select(UsuarioModel).filter_by(id=usuario_id)
        )).scalars().first()

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Usuário não encontrado.'
            )

        existing_token = (await db_session.execute(
            select(TokenDispositivoModel).filter_by(
                dispositivo_token=token_data_in.dispositivo_token)
        )).scalars().first()

        if existing_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Token já existe.'
            )

        token_data_out = TokenSchemaOut(id=str(uuid4()), **token_data_in.model_dump())
        token_data_model = TokenDispositivoModel(**token_data_out.model_dump(exclude={'usuario'}))
        token_data_model.usuario_id = usuario.pk_id

        db_session.add(token_data_model)
        await db_session.commit()
        await db_session.refresh(token_data_model)

        return token_data_out

    except IntegrityError as e:
        db_session.rollback()
        error_message = str(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ocorreu um erro ao inserir os dados no banco. Erro: {error_message}'
        )
