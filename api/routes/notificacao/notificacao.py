from fastapi import APIRouter, status, Depends
from api.routes.notificacao.schemas import NotificacaoIn, NotificacaoOut
from api.services.notificacao_service import (send_notification, enviar_notificacao_push, get_notificacoes,
                                              get_notficacao_nao_visualizadas, patch_marcar_como_visualizada)
from api.contrib.dependecies import DatabaseDependency
from api.routes.usuarios.dependecies import get_current_user


router = APIRouter()


@router.post(
    "/send-notification",
    summary='Enviar uma notificação',
    status_code=status.HTTP_201_CREATED,
    response_model=NotificacaoOut
)
async def enviar_notificacao(notification: NotificacaoIn, db_ession: DatabaseDependency):
    return await send_notification(db_ession, notification)


@router.post("/enviar_push")
def enviar_push(token: str, titulo: str, mensagem: str):
    """
    Endpoint para enviar notificações push via Firebase.
    """
    resultado = enviar_notificacao_push(token, titulo, mensagem)
    return resultado


@router.get('/notificacoes', response_model=list[NotificacaoOut])
async def listar_notificacoes(usuario_id: int, db_session: DatabaseDependency):
    return await get_notificacoes(usuario_id, db_session)


@router.get('/notificacoes/novas', response_model=list[NotificacaoOut])
async def listar_nao_visualizadas(usuario_id: str, db_session: DatabaseDependency):
    return await get_notficacao_nao_visualizadas(usuario_id, db_session)


@router.patch('/notificacoes/{notificacao_id}/visualizar')
async def marcar_como_visualizada(
        notificacao_id: str,
        usuario_id: str,
        db_session: DatabaseDependency
):
    return await patch_marcar_como_visualizada(notificacao_id, usuario_id, db_session)
