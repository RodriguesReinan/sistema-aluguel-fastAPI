from datetime import datetime, timedelta
from sqlalchemy.future import select
from api.services.notificacao_service import send_notification
from api.routes.contratos.models import ContratoModel
from api.routes.pagamento.models import PagamentoModel
from api.routes.inquilinos.models import InquilinoModel
from api.routes.tokens_dispositivos.token_model import TokenDispositivoModel
from api.routes.notificacao.schemas import NotificacaoIn
from api.db.database import get_session  # usado para o formato manual (testar_verificar_vencimentos.py)
import logging

# Configurando o logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def verificar_vencimentos(db_session):
    hoje = datetime.utcnow().date()

    pagamentos_query = select(PagamentoModel).where(
        PagamentoModel.data_pagamento.is_(None),  # ainda não foi pago
        PagamentoModel.data_vencimento.in_([
            hoje + timedelta(days=1),  # vence em um dia
            hoje,
            hoje - timedelta(days=3)  # Três dias após
        ])
    )

    pagamentos = (await db_session.execute(pagamentos_query)).scalars().all()

    if not pagamentos:
        logger.info(f"[Scheduler] Nenhum pagamento a verificar para {hoje}.")

    for pagamento in pagamentos:
        # Busca o contrato relacionado
        contrato = await db_session.execute(
            select(ContratoModel).where(ContratoModel.pk_id == pagamento.contrato_id)
        )
        contrato = contrato.scalars().first()

        if not contrato:
            logger.warning(f"[Scheduler] Contrato não encontrado para o pagamento {pagamento.pk_id}.")
            continue

        usuario_id = contrato.usuario_id
        logger.info(f"[Scheduler] Verificando vencimentos para o usuário ID: {usuario_id}.")

        # Busca o inquilino para usar o nome na mensagem
        inquilino = await db_session.execute(
            select(InquilinoModel).where(InquilinoModel.pk_id == contrato.inquilino_id)
        )
        inquilino = inquilino.scalars().first()

        if not inquilino:
            logger.warning(f"[Scheduler] Inquilino não encontrado para o contrato {contrato.pk_id}.")
            continue

        tokens = await db_session.execute(
            select(TokenDispositivoModel.dispositivo_token)
            .where(TokenDispositivoModel.usuario_id == usuario_id)
        )
        tokens = tokens.scalars().all()

        if not tokens:
            logger.warning(f"[Scheduler] Nenhum token encontrado para o usuário {usuario_id}.")
            continue  # Nenhum token encontrado para o usuário

        dias_para_vencimento = (pagamento.data_vencimento - hoje).days
        logger.info(f"[Scheduler] Dias para vencimento: {dias_para_vencimento}.")

        # Define tipo, título e mensagem da notificação
        if dias_para_vencimento == 1:
            tipo = 'vencimento'
            titulo = 'Aviso de Vencimento'
            mensagem = (
                f'O aluguel de {inquilino.nome} vence amanhã ({pagamento.data_vencimento.strftime("%d/%m/%Y")})')
        elif dias_para_vencimento == 0:
            tipo = 'vencimento'
            titulo = 'Vencimento hoje'
            mensagem = f'O aluguel de {inquilino.nome} vence hoje ({pagamento.data_vencimento.strftime("%d/%m/%Y")})'
        elif dias_para_vencimento == -3:
            tipo = 'atraso'
            titulo = 'Pagamento em atraso'
            mensagem = (
                f'O aluguel de {inquilino.nome} está atrasado há 3 dias '
                f'({pagamento.data_vencimento.strftime("%d/%m/%Y")})')
        else:
            logger.info(
                f"[Scheduler] Pulo a notificação para o pagamento {pagamento.pk_id}, sem data válida para notificação.")
            continue  # se por algum motivo caiu fora da lógica

        for token in tokens:
            notificacao = NotificacaoIn(
                pagamento_id=pagamento.pk_id,
                tipo_notificacao=tipo,
                data_envio=datetime.utcnow(),
                meio_envio='push',
                titulo=titulo,
                mensagem=mensagem,
                status='enviado-nao-visualizado',
                usuario_id=usuario_id,
                dispositivo_token=token
            )
            await send_notification(db_session, notificacao)

    logger.info("[Scheduler] Verificação de vencimentos concluída.")
    # Não é necessário fechar o db_session manualmente, o contexto `async for db_session in get_session()` cuida disso.



# import asyncio
# from datetime import datetime, timedelta
# from apscheduler.schedulers.background import BackgroundScheduler
# from sqlalchemy.future import select
# from api.services.notificacao_service import send_notification
# from api.routes.contratos.models import ContratoModel
# from api.routes.pagamento.models import PagamentoModel
# from api.routes.inquilinos.models import InquilinoModel
# from api.routes.tokens_dispositivos.token_model import TokenDispositivoModel
# from api.routes.notificacao.schemas import NotificacaoIn
# from api.contrib.dependecies import DatabaseDependency
# from api.db.database import get_session  # usado para o formato manual (testar_verificar_vencimentos.py)
#
#
# async def verificar_vencimentos(db_session):
#     hoje = datetime.utcnow().date()
#
#     pagamentos_query = select(PagamentoModel).where(
#         PagamentoModel.data_pagamento.is_(None),  # ainda não foi pago
#         PagamentoModel.data_vencimento.in_([
#             hoje + timedelta(days=1),  # vence em um dia
#             hoje,
#             hoje - timedelta(days=3)  # Tês dias após
#         ])
#     )
#
#     pagamentos = (await db_session.execute(pagamentos_query)).scalars().all()
#
#     for pagamento in pagamentos:
#         # Busca o contrato relacionado
#         contrato = (await db_session.execute(
#             select(ContratoModel).where(ContratoModel.pk_id == pagamento.contrato_id)
#         )).scalars().first()
#
#         if not contrato:
#             continue
#
#         usuario_id = contrato.usuario_id
#         print('usuario id scheduler: ', usuario_id)
#
#         # Busca o inquilino para usar o nome na mensagem
#         inquilino = (await db_session.execute(
#             select(InquilinoModel).where(InquilinoModel.pk_id == contrato.inquilino_id)
#         )).scalars().first()
#
#         if not inquilino:
#             continue
#
#         tokens = (await db_session.execute(
#             select(TokenDispositivoModel.dispositivo_token)
#             .where(TokenDispositivoModel.usuario_id == usuario_id)
#         )).scalars().all()
#
#         if not tokens:
#             continue  # Nenhum token encontrado para o usuário
#
#         dias_para_vencimento = (pagamento.data_vencimento - hoje).days
#         print('dias para vencimentos: ', dias_para_vencimento)
#
#         # Define tipo, título e mensagem da notificação
#         if dias_para_vencimento == 1:
#             tipo = 'vencimento'
#             titulo = 'Aviso de Vencimento'
#             mensagem = (f'O aluguel de {inquilino.nome} vence amanhã ('
#                         f'{pagamento.data_vencimento.strftime("%d/%m/%Y")})')
#         elif dias_para_vencimento == 0:
#             tipo = 'vencimento'
#             titulo = 'Vencimento hoje'
#             mensagem = (f'O aluguel de {inquilino.nome} vence hoje ('
#                         f'{pagamento.data_vencimento.strftime("%d/%m/%Y")})')
#         elif dias_para_vencimento == -3:
#             tipo = 'atraso'
#             titulo = 'Pagamento em atraso'
#             mensagem = (f'O aluguel de {inquilino.nome} está atrasado há 3 dias ('
#                         f'{pagamento.data_vencimento.strftime("%d/%m/%Y")})')
#         else:
#             continue  # se por algum motivo caiu fora da lógica
#
#         for token in tokens:
#             notificacao = NotificacaoIn(
#                 pagamento_id=pagamento.pk_id,
#                 tipo_notificacao=tipo,
#                 data_envio=datetime.utcnow(),
#                 meio_envio='push',
#                 titulo=titulo,
#                 mensagem=mensagem,
#                 status='enviado-nao-visualizado',
#                 usuario_id=usuario_id,
#                 dispositivo_token=token
#             )
#             await send_notification(db_session, notificacao)
#     await db_session.close()
#
# #
# # # ✅ Wrapper para o APScheduler
# # def agendar_verificacao_vencimentos():
# #     asyncio.run(run_verificacao())
# #
# #
# # async def run_verificacao():
# #     async for session in get_session():
# #         await verificar_vencimentos(session)
# #         break
# #
# #
# # scheduler = BackgroundScheduler()
# # # scheduler.add_job(verificar_vencimentos, 'cron', hour=0, minute=0)  # Executa diariamente à meia-noite
# # scheduler.add_job(agendar_verificacao_vencimentos, 'cron', hour=0, minute=0)  # Executa diariamente à meia-noite
# # scheduler.start()
# #
# #
# # async def manter_scheduler_rodando():
# #     print("🕐 Agendador ativo. Pressione Ctrl+C para sair.")
# #     try:
# #         while True:
# #             await asyncio.sleep(1)  # espera assíncrona, leve para o sistema
# #     except (KeyboardInterrupt, SystemExit):
# #         print("⛔ Encerrando scheduler...")
# #         scheduler.shutdown()
# #
# #
# # if __name__ == "__main__":
# #     asyncio.run(manter_scheduler_rodando())
