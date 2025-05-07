from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from api.routes.usuarios.schemas.usuario_schema import UserIn, Token, UserOut
from api.services.usuario_service import register, login, get_all_usuarios, get_usuario
from api.routes.usuarios.dependecies import get_current_user
from api.contrib.dependecies import DatabaseDependency


router = APIRouter()


@router.post(
    "/register-user",
    summary='Criar um usuário',
    status_code=status.HTTP_201_CREATED,
    response_model=Token)
async def criar_usuario(db_session: DatabaseDependency, usuario_in: UserIn,
                        current_user: UserOut = Depends(get_current_user)
                        ):
    return await register(db_session, usuario_in)


@router.post("/login",
             summary='Fazer login',
             status_code=status.HTTP_201_CREATED,
             response_model=Token)
async def fazer_login(db_session: DatabaseDependency, form_data: OAuth2PasswordRequestForm = Depends()):  # , user_login_in: UserLogin
    return await login(db_session, form_data)


@router.get(
    '/usuarios',
    summary='Consultar todos os usuários',
    status_code=status.HTTP_200_OK,
    response_model=list[UserOut]
)
async def listar_usuarios(db_session: DatabaseDependency, current_user: UserOut = Depends(get_current_user)):
    return await get_all_usuarios(db_session)


@router.get(
    path='/{id}',
    summary='Consultar um usuário',
    status_code=status.HTTP_200_OK,
    response_model=UserOut,
)
async def listar_usuario_id(id:str, db_session: DatabaseDependency, current_user: UserOut = Depends(get_current_user)):
    return await get_usuario(id, db_session)


@router.get(
    "/dados/me",
    summary='Retorna os dados do usuário logado',
    status_code=status.HTTP_200_OK,
    response_model=UserOut
)
async def get_me(current_user: UserOut = Depends(get_current_user)):
    return current_user


# @router.post("/refresh", response_model=Token)
# def refresh_token(refresh_token: Depends(oauth2_scheme), db_session: DatabaseDependency):
#     payload = decode_token(refresh_token)
#     if not payload or payload.get("type") != "refresh":
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido")
#     email = payload.get("sub")
#     user = db_session.query(UserModel).filter(UserModel.email == email).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")
#     access_token = create_access_token({"sub": user.email})
#     new_refresh_token = create_refresh_token({"sub": user.email})  # Opcional: renovar o refresh token
#     return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}
#
#
# # Função para verificar se o token está na blacklist
# def is_token_blacklisted(token: str, db_session: DatabaseDependency):
#     return db_session.query(TokenBlacklist).filter(TokenBlacklist.token == token).first() is not None
#
#
# # Adicionar ao início do controller
# @router.post("/logout")
# def logout(token: str = Depends(oauth2_scheme), db_session: DatabaseDependency = Depends()):
#     payload = decode_token(token)
#     if not payload:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
#     if is_token_blacklisted(token, db_session):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token já invalidado")
#     expires_at = datetime.utcfromtimestamp(payload["exp"])
#     blacklisted_token = TokenBlacklist(token=token, expires_at=expires_at)
#     try:
#         db_session.add(blacklisted_token)
#         db_session.commit()
#         return {"message": "Logout realizado com sucesso"}
#     except Exception:
#         db_session.rollback()
#         raise HTTPException(status_code=500, detail="Erro ao realizar logout")
#
#
# # Atualizar get_current_user para verificar blacklist
# def get_current_user(token: str = Depends(oauth2_scheme), db_session: DatabaseDependency = Depends()):
#     if is_token_blacklisted(token, db_session):
#         raise HTTPException(status_code=401, detail="Token inválido (blacklisted)")
#     payload = decode_token(token)
#     if not payload or payload.get("type") != "access":
#         raise HTTPException(status_code=401, detail="Token inválido")
#     email = payload.get("sub")
#     if email is None:
#         raise HTTPException(status_code=401, detail="Token inválido")
#     user = db_session.query(UserModel).filter(UserModel.email == email).first()
#     if user is None:
#         raise HTTPException(status_code=401, detail="Usuário não encontrado")
#     return user
