from dateutil.relativedelta import relativedelta
from datetime import date
from api.routes.contratos.models import ContratoModel
from api.routes.pagamento.models import PagamentoModel
from api.routes.pagamento.schemas import PagamentoOut, PagamentoUpdate
from api.contrib.dependecies import DatabaseDependency
from sqlalchemy.future import select
from fastapi import HTTPException, status
import calendar
from api.routes.usuarios.models.usuario_model import UsuarioModel
from api.contrib.tenancy import filter_by_tenant


async def criar_pagamentos_para_contratos(contrato: ContratoModel, db_session: DatabaseDependency,
                                          current_user: UsuarioModel):
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

    data_vencimento = ajustar_data_vencimento(contrato.data_inicio, int(contrato.dia_vencimento))

    while data_vencimento <= contrato.data_fim:
        pagamento = PagamentoModel(
            contrato_id=contrato.pk_id,
            valor_pago=0.0,
            data_vencimento=data_vencimento,
            data_pagamento=None,
            metodo_pagamento=None,
            status='pendente',
            tenant_id=current_user.id
        )
        pagamentos.append(pagamento)

        # Adiciona um mês ao vencimento mantendo o mesmo dia do mês
        # Próximo mês, ajustando novamente o dia se necessário
        proxima_data_base = data_vencimento + relativedelta(months=1)
        data_vencimento = ajustar_data_vencimento(proxima_data_base, contrato.dia_vencimento)

    db_session.add_all(pagamentos)
    # await db_session.commit()


async def get_all_pagamentos(db_session: DatabaseDependency, current_user: UsuarioModel) -> list[PagamentoOut]:
    # pagamentos: list[PagamentoOut] = (await db_session.execute(select(PagamentoModel))).scalars().all()

    statement = select(PagamentoModel).filter(PagamentoModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)
    pagamentos = (await db_session.execute(statement)).scalars().all()

    return pagamentos


async def get_pagamento_por_contrato(contrato_id: str, db_session: DatabaseDependency,
                                     current_user: UsuarioModel) -> list[PagamentoOut]:
    # Buscar contrato pelo UUID para obter o pk_id
    # contrato = (await db_session.execute(
    #     select(ContratoModel).filter_by(id=contrato_id)
    # )).scalars().first()

    statement = select(ContratoModel).filter(ContratoModel.id == contrato_id, ContratoModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)
    contrato = (await db_session.execute(statement)).scalars().first()

    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Contrato {contrato_id} não encontrado'
        )

    # Agora buscar os pagamentos pelo pk_id
    # pagamentos: list[PagamentoOut] = (await db_session.execute(
    #     select(PagamentoModel).filter_by(contrato_id=contrato.pk_id)
    # )).scalars().all()

    statement = select(PagamentoModel).filter(PagamentoModel.contrato_id == contrato.pk_id, PagamentoModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)
    pagamentos = (await db_session.execute(statement)).scalars().all()

    if not pagamentos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Pagamento de aluguel não encontrado no id {contrato_id}'
        )

    return pagamentos


async def patch_pagamento(
        pagamento_id: str,
        db_session: DatabaseDependency,
        pagamento_up: PagamentoUpdate,
        current_user: UsuarioModel
        ) -> PagamentoOut:

    statement = select(PagamentoModel).filter(PagamentoModel.id == pagamento_id, PagamentoModel.ativo == 1)
    statement = filter_by_tenant(statement, current_user.id)
    pagamento = (await db_session.execute(statement)).scalars().first()

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


async def atualizar_pagamentos(aluguel: ContratoModel, data_fim_antiga: date, nova_data_fim: date,
                               db_session: DatabaseDependency, current_user: UsuarioModel):
    try:
        # Função auxiliar para ajustar a data de vencimento
        def ajustar_data_vencimento(base_date: date, dia_vencimento: int) -> date:
            ano = base_date.year
            mes = base_date.month
            ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
            dia = min(dia_vencimento, ultimo_dia_mes)
            return base_date.replace(day=dia)

        # Se a data de fim aumentou, criar novas parcelas
        if nova_data_fim > data_fim_antiga:
            pagamentos = []

            # Obter a última data de vencimento já cadastrada
            statement = select(PagamentoModel.data_vencimento).filter(
                PagamentoModel.contrato_id == aluguel.pk_id
            ).order_by(PagamentoModel.data_vencimento.desc())

            ultima_parcela = (await db_session.execute(statement)).scalars().first()

            # Calcular a próxima data de vencimento a partir da última registrada
            data_vencimento = ajustar_data_vencimento(ultima_parcela + relativedelta(months=1), aluguel.dia_vencimento)

            while data_vencimento <= nova_data_fim:
                pagamento = PagamentoModel(
                    contrato_id=aluguel.pk_id,
                    valor_pago=0.0,
                    data_vencimento=data_vencimento,
                    data_pagamento=None,
                    metodo_pagamento=None,
                    status='pendente',
                    tenant_id=current_user.id
                )
                pagamentos.append(pagamento)

                # Próximo mês, mantendo o mesmo dia de vencimento
                proxima_data_base = data_vencimento + relativedelta(months=1)
                data_vencimento = ajustar_data_vencimento(proxima_data_base, aluguel.dia_vencimento)

            db_session.add_all(pagamentos)
            # await db_session.commit()

        # Se a data de fim diminuiu, remover parcelas futuras
        elif nova_data_fim < data_fim_antiga:
            statement = select(PagamentoModel).filter(
                PagamentoModel.contrato_id == aluguel.pk_id,
                PagamentoModel.data_vencimento > nova_data_fim,
                PagamentoModel.status == 'pendente'
            )
            parcelas_excedentes = (await db_session.execute(statement)).scalars().all()

            for parcela in parcelas_excedentes:
                await db_session.delete(parcela)

            await db_session.commit()

    except Exception as e:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Erro ao atualizar os pagamentos: {str(e)}'
        )
