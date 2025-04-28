from fastapi import APIRouter, status, Depends
from api.routes.pagamento.schemas import PagamentoOut, PagamentoUpdate
from api.routes.pagamento.pagamentos_contratos import get_all_pagamentos, get_pagamento_por_contrato, patch_pagamento
from api.contrib.dependecies import DatabaseDependency
from api.routes.usuarios.dependecies import get_current_user
from api.routes.usuarios.models.usuario_model import UsuarioModel


router = APIRouter()


@router.get(
    path='/',
    summary='Consultar todos os pagamentos',
    status_code=status.HTTP_200_OK,
    response_model=list[PagamentoOut],
)
async def listar_pagamentos(db_session: DatabaseDependency, current_user: UsuarioModel = Depends(get_current_user)):
    return await get_all_pagamentos(db_session, current_user)


@router.get(
    path='/contrato/{contrato_id}',
    summary='Consultar pagamentos de um contrato específico',
    status_code=status.HTTP_200_OK,
    response_model=list[PagamentoOut],
)
async def listar_pagamento_por_contrato(contrato_id: str, db_session: DatabaseDependency,
                                        current_user: UsuarioModel = Depends(get_current_user)):
    return await get_pagamento_por_contrato(contrato_id, db_session, current_user)


@router.patch(
    '/{pagamento_id}',
    summary='Editar um pagamento pelo id.',
    status_code=status.HTTP_200_OK,
    response_model=PagamentoOut,
)
async def editar_pagamento(pagamento_id: str, db_session: DatabaseDependency, pagamento_up: PagamentoUpdate,
                           current_user: UsuarioModel = Depends(get_current_user)):
    return await patch_pagamento(pagamento_id, db_session, pagamento_up, current_user)
