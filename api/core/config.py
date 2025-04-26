import os
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    DB_URL: str  # vaiárvel de ambiente no ..env
    # DB_URL: str = Field(default='mysql+aiomysql://root:suaSenha@host/seuBancoDados')


settings = Settings()


