from fastapi import FastAPI
from routers import api_router
from fastapi.middleware.cors import CORSMiddleware

# api.main:app   -- rodar o servidor uvcorn
# api.main:app --reload   -- rodar o servidor uvcorn com reload automático

app = FastAPI(title='Sistema de Gerenciamento de Aluguéis')
app.include_router(api_router)


# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modifique para restringir domínios específicos
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)


if __name__ == 'main':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8000, log_level='info', reload=False)
