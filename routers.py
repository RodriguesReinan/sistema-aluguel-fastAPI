from fastapi import APIRouter
from api.routes.proprietarios.proprietarios import router as proprietario
from api.routes.imoveis.imoveis import router as imovel
from api.routes.inquilinos.inquilinos import router as inquilino
from api.routes.contratos.contrato import router as contrato
from api.routes.notificacao.notificacao import router as notificacao
from api.routes.usuarios.controllers.usuario import router as users
from api.routes.tokens_dispositivos.token_controller import router as tokens_dispositivos
from api.routes.pagamento.pagamentos_controller import router as pagamentos
from api.routes.contrato_pdf_export.contrato_pdf import router as contratos_pf

api_router = APIRouter()

api_router.include_router(proprietario, prefix="/proprietarios", tags=["Proprietários"])
api_router.include_router(imovel, prefix='/imoveis', tags=['Imóveis'])
api_router.include_router(inquilino, prefix='/inquilinos', tags=['Inquilinos'])
api_router.include_router(contrato, prefix='/contrato-aluguel', tags=['Contratos Aluguéis'])
api_router.include_router(notificacao, prefix='/notificacao', tags=['Notificações'])
api_router.include_router(users, prefix='/auth', tags=['Autenticação'])
api_router.include_router(tokens_dispositivos, prefix='/tokens-dispositivos', tags=['Tokens Dispositivos'])
api_router.include_router(pagamentos, prefix='/pagamentos', tags=['Pagamentos'])
api_router.include_router(contratos_pf, prefix='/contrato-pdf', tags=['Contrato PDF'])
