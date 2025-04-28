from fastapi import status
from api.routes.notificacao.models import NotificacaoModel
from api.routes.notificacao.schemas import NotificacaoIn, NotificacaoOut
from api.routes.usuarios.models.usuario_model import UsuarioModel
from api.contrib.tenancy import filter_by_tenant
from sqlalchemy.future import select
from fastapi import HTTPException
from api.contrib.dependecies import DatabaseDependency
import firebase_admin
from firebase_admin import credentials, messaging


# Caminho do arquivo JSON da conta de serviço
FIREBASE_CREDENTIALS_PATH = "FIREBASE_CREDENTIALS_PATH.json"


# Verifica se o Firebase já foi inicializado para evitar erros
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)


def enviar_notificacao_push(token: str, titulo: str, mensagem: str):
    """
    Envia uma notificação push via Firebase Cloud Messaging.

    :param token: Token do dispositivo que receberá a notificação.
    :param titulo: Título da notificação.
    :param mensagem: Corpo da mensagem.
    :return: Resposta do Firebase.
    """
    try:
        message = messaging.Message(
            token=token,
            notification=messaging.Notification(
                title=titulo,
                body=mensagem
            )
        )

        response = messaging.send(message)
        return {"status": "sucesso", "response": response}
    except Exception as e:
        return {"status": "erro", "message": str(e)}


async def send_notification(db_session: DatabaseDependency, notification: NotificacaoIn,
                            current_user: UsuarioModel) -> NotificacaoOut:
    try:

        # Enviar via Firebase SDK
        resultado = enviar_notificacao_push(
            token=notification.dispositivo_token,
            titulo=notification.titulo,
            mensagem=notification.mensagem
        )

        if resultado["status"] != "sucesso":
            raise Exception(resultado["message"])

        # Salvar no banco
        notificacao = NotificacaoModel(
            pagamento_id=notification.pagamento_id,
            tipo_notificacao=notification.tipo_notificacao,
            data_envio=notification.data_envio,
            meio_envio=notification.meio_envio,
            titulo=notification.titulo,
            mensagem=notification.mensagem,
            status='enviado-nao-visualizado',
            usuario_id=notification.usuario_id,
            tenant_id=current_user.id
            # dispositivo_token=notification.dispositivo_token  # se eu quiser salvar o token no banco, mudar o model
        )
        db_session.add(notificacao)
        await db_session.commit()
        await db_session.refresh(notificacao)

        # return NotificacaoOut(**notificacao.__dict__)
        return NotificacaoOut.model_validate(notificacao)

    except Exception as e:
        await db_session.rollback()
        erro_message = str(e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ocorreu algum erro ao enviar a notificação. Erro: {erro_message}'
        )


async def get_notificacoes(usuario_id: int, db_session: DatabaseDependency,
                           current_user: UsuarioModel) -> list[NotificacaoOut]:
    # notificacoes: list[NotificacaoOut] = (await db_session.execute(
    #     select(NotificacaoModel).filter(NotificacaoModel.usuario_id == usuario_id).order_by(
    #         NotificacaoModel.data_envio.desc()
    #     )
    # )).scalars().all()

    statement = select(NotificacaoModel).filter(NotificacaoModel.usuario_id == usuario_id).order_by(
        NotificacaoModel.data_envio.desc()
    )
    statement = filter_by_tenant(statement, current_user.id)
    notificacoes = (await db_session.execute(statement)).scalars().all()

    return notificacoes


async def get_notficacao_nao_visualizadas(usuario_id: str, db_session: DatabaseDependency,
                                          current_user: UsuarioModel) -> list[NotificacaoOut]:
    # usuario = (await db_session.execute(
    #     select(UsuarioModel).filter_by(id=usuario_id)
    # )).scalars().first()

    statement = select(UsuarioModel).filter(UsuarioModel.id == usuario_id, UsuarioModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)
    usuario = (await db_session.execute(statement)).scalars().first()

    # notificacoes: list[NotificacaoOut] = (await db_session.execute(
    #     select(NotificacaoModel)
    #     .filter(NotificacaoModel.usuario_id == usuario.pk_id)
    #     .filter(NotificacaoModel.status != 'enviado-visualizado')
    #     .order_by(NotificacaoModel.data_envio.desc())
    # )).scalars().all()

    statement = (
        select(NotificacaoModel).filter(
            NotificacaoModel.usuario_id == usuario.pk_id,
            NotificacaoModel.status != 'enviado-visualizado',
            NotificacaoModel.ativo == 1
        )
    )
    statement = filter_by_tenant(statement, current_user.id)
    notificacoes = (await db_session.execute(statement)).scalars().all()

    return notificacoes


async def patch_marcar_como_visualizada(notificacao_id, usuario_id, db_session, current_user: UsuarioModel):
    # usuario = (await db_session.execute(
    #     select(UsuarioModel).filter_by(id=usuario_id)
    # )).scalars().first()

    statement = select(UsuarioModel).filter(UsuarioModel.id == usuario_id, UsuarioModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)

    usuario = (await db_session.execute(statement)).scalars().first()

    # notificacao = (await db_session.execute(
    #     select(NotificacaoModel)
    #     .filter(NotificacaoModel.id == notificacao_id)
    # )).scalars().first()

    statement = (
        select(NotificacaoModel).filter(
            NotificacaoModel.id == notificacao_id,
            NotificacaoModel.ativo == 1
        )
    )
    statement = filter_by_tenant(statement, current_user.id)
    notificacao = (await db_session.execute(statement)).scalars().first()

    if not notificacao or notificacao.usuario_id != usuario.pk_id:
        print(f'dentro do if not notificação: notificação id: {notificacao.usuario_id} - usuario_id: {usuario_id}')
        raise HTTPException(status_code=404, detail="Notificação não encontrada")

    notificacao.status = 'enviado-visualizado'
    await db_session.commit()
    return {"ok": True}
