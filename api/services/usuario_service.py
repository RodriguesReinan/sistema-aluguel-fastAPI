from datetime import datetime
from uuid import uuid4

from fastapi.security import OAuth2PasswordRequestForm

from api.routes.usuarios.schemas.usuario_schema import UserIn, Token, UserLogin, UserOut
from fastapi import status, Body, HTTPException
from api.routes.usuarios.models.usuario_model import UsuarioModel
from api.core.security import (hash_password, create_access_token, create_refresh_token)
from sqlalchemy.future import select
from api.contrib.dependecies import DatabaseDependency
from api.core.security import verify_password


async def register(
        db_session: DatabaseDependency,
        usuario_in: UserIn = Body(...)
) -> Token:
    user_email = usuario_in.email

    email_verify = (await db_session.execute(
        select(UsuarioModel).filter_by(email=user_email)
    )).scalars().first()
    if email_verify:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já registrado")

    hashed_password = hash_password(usuario_in.hashed_password)

    user_model = UsuarioModel(id=str(uuid4()),
                              username=usuario_in.username,
                              email=usuario_in.email,
                              hashed_password=hashed_password
                              )

    db_session.add(user_model)
    await db_session.commit()
    await db_session.refresh(user_model)
    access_token = create_access_token({"sub": usuario_in.email})
    refresh_token = create_refresh_token({"sub": usuario_in.email})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


async def login(
        db_ession: DatabaseDependency,
        user_data: OAuth2PasswordRequestForm,
        # user_data: UserLogin
) -> Token:
    user = (await db_ession.execute(
        select(UsuarioModel).filter_by(email=user_data.username)
    )).scalars().first()

    # breakpoint()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )
    # return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


async def get_all_usuarios(db_session: DatabaseDependency) -> list[UserOut]:
    usuarios: list[UserOut] = (await db_session.execute(
        select(UsuarioModel)
    )).scalars().all()

    return usuarios


async def get_usuario(id: str, db_session: DatabaseDependency) -> UserOut:
    usuario: UserOut = (await db_session.execute(
        select(UsuarioModel).filter_by(id=id)
        )).scalars().first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Usuário não encontrado no id {id}'
        )
    return usuario
