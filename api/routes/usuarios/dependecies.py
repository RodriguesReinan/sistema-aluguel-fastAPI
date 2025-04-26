from fastapi import Depends, HTTPException, Security
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from api.routes.usuarios.models.usuario_model import UsuarioModel
from api.core.security import SECRET_KEY, ALGORITHM
from api.contrib.dependecies import DatabaseDependency

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
        db_session: DatabaseDependency,
        token: str = Depends(oauth2_scheme)
        ):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise HTTPException(status_code=401, detail="Token inválido")

        user = (await db_session.execute(
            select(UsuarioModel).filter(UsuarioModel.email == user_email)
        )).scalars().first()
        print(user)

        if user is None:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")

        return user
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Token inválido")

