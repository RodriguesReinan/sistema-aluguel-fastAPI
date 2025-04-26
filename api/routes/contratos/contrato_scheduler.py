from datetime import date
from sqlalchemy.future import select
from api.routes.contratos.models import ContratoModel


async def encerrar_contratos_expirados(db_session):
    hoje = date.today()
    result = await db_session.execute(
        select(ContratoModel).where(
            ContratoModel.data_fim < hoje,
            ContratoModel.status == "ativo"
        )
    )
    contratos = result.scalars().all()

    for contrato in contratos:
        contrato.status = "encerrado"

    if contratos:
        await db_session.commit()
