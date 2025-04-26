from pydantic import EmailStr, Field
from api.contrib.schemas import BaseSchema, OutMixin


class UserCreate(BaseSchema):
    username: str = Field(description='Nome do usuáiro', min_length=5)
    email: EmailStr
    hashed_password: str = Field(description='Senha do usuáiro', min_length=8)


class UserIn(UserCreate):
    pass


class UserOut(OutMixin):
    username: str
    email: EmailStr


class UsuarioContrato(OutMixin):
    pass


class UserTokenDispositivo(OutMixin):
    pass


class UserLogin(BaseSchema):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class Token(BaseSchema):
    access_token: str
    token_type: str
    refresh_token: str

