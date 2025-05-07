from fastapi import FastAPI
from routers import api_router
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import os

# api.main:app   -- rodar o servidor uvcorn
# api.main:app --reload   -- rodar o servidor uvcorn com reload automático


# Detectar ambiente
ENV = os.getenv("ENV", "dev")

# Definir o caminho do .env dependendo do ambiente
if ENV == "prod":
    dotenv_path = Path(__file__).resolve().parents[1] / '.env'  # para quando está fora de /backend
else:
    dotenv_path = Path(__file__).resolve().parent / '.env'  # dentro do /backend

# Carregar variáveis do .env
load_dotenv(dotenv_path)

app = FastAPI(title='Sistema de Gerenciamento de Aluguéis')
app.include_router(api_router)

# Lista de domínios que podem acessar a API
origins = [
    "http://localhost",  # Navegadores como o Chrome usam isso
    "http://localhost:4200",  # Angular geralmente roda nessa porta
    "http://imoveis.rrdigitalsolution.online",
    "https://imoveis.rrdigitalsolution.online",  # caso use HTTPS
]


# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Modifique para restringir domínios específicos
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8000, log_level='info', reload=False)
