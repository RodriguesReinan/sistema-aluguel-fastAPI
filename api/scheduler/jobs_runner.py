import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from api.routes.notificacao.notificacao_scheduler import verificar_vencimentos
from api.routes.contratos.contrato_scheduler import encerrar_contratos_expirados
from api.db.database import get_session
from api.utils.logger import logger  # ← logger importado


async def wrapper(task_func, task_name: str):
    try:
        async for db_session in get_session():
            await task_func(db_session)
            logger.info(f"Tarefa '{task_name}' executada com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao executar tarefa '{task_name}': {e}", exc_info=True)


def main():
    scheduler = AsyncIOScheduler()

    scheduler.add_job(lambda: asyncio.create_task(wrapper(verificar_vencimentos, "verificar_vencimentos")),
                      'cron', hour=0)
    scheduler.add_job(lambda: asyncio.create_task(wrapper(encerrar_contratos_expirados,
                                                          "encerrar_contratos_expirados")), 'cron', hour=1)

    scheduler.start()
    logger.info("✅ Schedulers iniciados.")

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Encerrando schedulers.")
        scheduler.shutdown()
