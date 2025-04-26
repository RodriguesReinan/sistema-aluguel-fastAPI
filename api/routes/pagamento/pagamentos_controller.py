from fastapi import APIRouter, status, Depends
from api.routes.pagamento.schemas import PagamentoOut, PagamentoUpdate
from api.routes.pagamento.pagamentos_contratos import get_all_pagamentos, get_pagamento_por_contrato, patch_pagamento
from api.contrib.dependecies import DatabaseDependency


router = APIRouter()


@router.get(
    path='/',
    summary='Consultar todos os pagamentos',
    status_code=status.HTTP_200_OK,
    response_model=list[PagamentoOut],
)
async def listar_pagamentos(db_session: DatabaseDependency):
    return await get_all_pagamentos(db_session)


@router.get(
    path='/contrato/{contrato_id}',
    summary='Consultar pagamentos de um contrato específico',
    status_code=status.HTTP_200_OK,
    response_model=list[PagamentoOut],
)
async def listar_pagamento_por_contrato(contrato_id: str, db_session: DatabaseDependency):
    return await get_pagamento_por_contrato(contrato_id, db_session)


@router.patch(
    '/{pagamento_id}',
    summary='Editar um pagamento pelo id.',
    status_code=status.HTTP_200_OK,
    response_model=PagamentoOut,
)
async def edite_pagamento(pagamento_id: str, db_session: DatabaseDependency, pagamento_up: PagamentoUpdate):
    return await patch_pagamento(pagamento_id, db_session, pagamento_up)
