from pydantic import EmailStr, Field, field_validator
from api.contrib.schemas import BaseSchema, OutMixin


class UserCreate(BaseSchema):
    username: str = Field(description='Nome do usuáiro', min_length=5)
    email: EmailStr
    hashed_password: str = Field(description='Senha do usuáiro', min_length=8)

    @field_validator('*')
    def check_empty_strings(cls, value, info):
        if isinstance(value, str) and value.strip() == "":
            raise ValueError(f"O campo '{info.field_name}' não pode ser vazio.")
        return value


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

