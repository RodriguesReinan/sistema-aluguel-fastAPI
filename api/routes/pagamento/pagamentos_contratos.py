from dateutil.relativedelta import relativedelta
from datetime import date
from api.routes.contratos.models import ContratoModel
from api.routes.pagamento.models import PagamentoModel
from api.routes.pagamento.schemas import PagamentoOut, PagamentoUpdate
from api.contrib.dependecies import DatabaseDependency
from sqlalchemy.future import select
from fastapi import HTTPException, status
import calendar


async def criar_pagamentos_para_contratos(contrato: ContratoModel, db_session: DatabaseDependency):
    pagamentos = []

    def ajustar_data_vencimento(base_date: date, dia_vencimento: int) -> date:
        """Garantir que uma data com o dia de vencimento desejado seja válida, mesmo em meses com menos dias
        (como fevereiro). Se o dia for inválido (ex: dia 31 em fevereiro),
        ela ajusta automaticamente para o último dia do mês."""

        ano = base_date.year
        mes = base_date.month

        # Essa linha usa a função calendar.monthrange(ano, mes) que retorna uma tupla:
        # (primeiro_dia_semana, total_de_dias_no_mes) - Então, [1] pega o número total de dias do mês.
        ultimo_dia_mes = calendar.monthrange(ano, mes)[1]

        # Esta linha diz: “Escolha o menor valor entre dia_vencimento (o dia desejado) e
        # ultimo_dia (o número máximo de dias do mês atual).”
        dia = min(dia_vencimento, ultimo_dia_mes)

        return base_date.replace(day=dia)

    # data_vencimento = contrato.data_inicio.replace(day=contrato.dia_vencimento)
    data_vencimento = ajustar_data_vencimento(contrato.data_inicio, int(contrato.dia_vencimento))

    while data_vencimento <= contrato.data_fim:
        pagamento = PagamentoModel(
            contrato_id=contrato.pk_id,
            valor_pago=0.0,
            data_vencimento=data_vencimento,
            data_pagamento=None,
            metodo_pagamento=None,
            status='pendente'
        )
        pagamentos.append(pagamento)

        # Adiciona um mês ao vencimento mantendo o mesmo dia do mês
        # Próximo mês, ajustando novamente o dia se necessário
        proxima_data_base = data_vencimento + relativedelta(months=1)
        data_vencimento = ajustar_data_vencimento(proxima_data_base, contrato.dia_vencimento)
        # data_vencimento += relativedelta(months=1)

    db_session.add_all(pagamentos)
    await db_session.commit()


async def get_all_pagamentos(db_session: DatabaseDependency) -> list[PagamentoOut]:
    pagamentos: list[PagamentoOut] = (await db_session.execute(select(PagamentoModel))).scalars().all()

    return pagamentos


async def get_pagamento_por_contrato(contrato_id: str, db_session: DatabaseDependency) -> list[PagamentoOut]:
    # Buscar contrato pelo UUID para obter o pk_id
    contrato = (await db_session.execute(
        select(ContratoModel).filter_by(id=contrato_id)
    )).scalars().first()

    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Contrato {contrato_id} não encontrado'
        )

    # Agora buscar os pagamentos pelo pk_id
    pagamentos: list[PagamentoOut] = (await db_session.execute(
        select(PagamentoModel).filter_by(contrato_id=contrato.pk_id)
    )).scalars().all()

    if not pagamentos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Pagamento de aluguel não encontrado no id {contrato_id}'
        )

    return pagamentos


async def patch_pagamento(
        pagamento_id: str,
        db_session: DatabaseDependency,
        pagamento_up: PagamentoUpdate
        ) -> PagamentoOut:

    pagamento: PagamentoOut = (await db_session.execute(
        select(PagamentoModel).filter_by(id=pagamento_id)
    )).scalars().first()

    if not pagamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Pagamento ID {pagamento_id} não encontrado.'
        )

    pagamento_update = pagamento_up.model_dump(exclude_unset=True)
    for key, value in pagamento_update.items():
        setattr(pagamento, key, value)

    await db_session.commit()
    await db_session.refresh(pagamento)

    return pagamento
