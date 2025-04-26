from dateutil.relativedelta import relativedelta
from num2words import num2words
from fastapi import status, HTTPException
from sqlalchemy.future import select
from api.routes.contrato_pdf_export.models import ContratoModeloPdfModel
from api.routes.contrato_pdf_export.schemas import ContratoCreate, ContratoUpdate
from api.utils.formatacao_valor_br import formatar_valor_br
from api.contrib.dependecies import DatabaseDependency
from api.routes.inquilinos.models import InquilinoModel
from api.routes.imoveis.models import ImovelModel
from api.routes.contratos.models import ContratoModel
from api.routes.proprietarios.models import ProprietarioModel
from datetime import datetime
import locale


async def criar_contrato(db_session: DatabaseDependency, contrato_data: ContratoCreate):
    try:
        contrato = ContratoModeloPdfModel(**contrato_data.dict())
        db_session.add(contrato)
        await db_session.commit()
        await db_session.refresh(contrato)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ocorreu um erro ao inserir os dados no banco. Erro: {e}'
        )

    return contrato


async def listar_contratos(db_session: DatabaseDependency):
    contratos_pdf = (await db_session.execute(
        select(ContratoModeloPdfModel).filter(ContratoModeloPdfModel.ativo == 1)
    )).scalars().all()

    return contratos_pdf


async def obter_contrato(db_session: DatabaseDependency, contrato_id: str):
    # result = (await db_session.execute(
    #     select(ContratoModeloPdfModel).filter_by(id=contrato_id)
    # )).scalars().first()

    result = (await db_session.execute(
        select(ContratoModeloPdfModel).filter(
                ContratoModeloPdfModel.id == contrato_id,
                ContratoModeloPdfModel.ativo == 1
        )
    )).scalars().first()

    return result


async def atualizar_modelo_contrato(db_session: DatabaseDependency, contrato_id: str, contrato_update: ContratoUpdate):
    # modelo = (await db_session.execute(
    #     select(ContratoModeloPdfModel).filter_by(id=contrato_id)
    # )).scalars().first()

    modelo = (await db_session.execute(
        select(ContratoModeloPdfModel).filter(
                ContratoModeloPdfModel.id == contrato_id,
                ContratoModeloPdfModel.ativo == 1
        )
    )).scalars().first()

    if modelo:
        modelo.conteudo_html = contrato_update.conteudo_html
        await db_session.commit()
        await db_session.refresh(modelo)
    return modelo


async def montar_dados_contrato(contrato_id: str, contrato_aluguel_id: str, db_session: DatabaseDependency) -> dict:
    # contrato_aluguel = (await db_session.execute(
    #     select(ContratoModel).filter_by(id=contrato_aluguel_id)
    # )).scalars().first()

    contrato_aluguel = (await db_session.execute(
        select(ContratoModel).filter(
            ContratoModel.id == contrato_aluguel_id,
            ContratoModel.ativo == 1
        )
    )).scalars().first()

    if not contrato_aluguel:
        raise HTTPException(
            status_code=404,
            detail='Contrato não encontrado.'
        )
    # inquilino = (await db_session.execute(
    #     select(InquilinoModel).filter_by(pk_id=contrato_aluguel.inquilino_id)
    # )).scalars().first()

    inquilino = (await db_session.execute(
        select(InquilinoModel).filter(
            InquilinoModel.pk_id == contrato_aluguel.inquilino_id,
            InquilinoModel.ativo == 1
        )
    )).scalars().first()

    # imovel = (await db_session.execute(
    #     select(ImovelModel).filter_by(pk_id=contrato_aluguel.imovel_id)
    # )).scalars().first()

    imovel = (await db_session.execute(
        select(ImovelModel).filter(
            ImovelModel.pk_id == contrato_aluguel.imovel_id,
            ImovelModel.ativo == 1
        )
    )).scalars().first()

    # proprietario = (await db_session.execute(
    #     select(ProprietarioModel).filter_by(pk_id=imovel.proprietario_id)
    # )).scalars().first()

    proprietario = (await db_session.execute(
        select(ProprietarioModel).filter(
            ProprietarioModel.pk_id == imovel.proprietario_id,
            ProprietarioModel.ativo == 1
        )
    )).scalars().first()

    # Configura o locale para português do Brasil
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

    # Obtém a data atual e formata
    data_assinatura_contrato = contrato_aluguel.created_at.strftime('%d de %B de %Y')

    valor_aluguel = contrato_aluguel.valor_mensal
    valor_formatado = formatar_valor_br(valor_aluguel)  # Esta função formata os valores para a moeda brasileira

    if isinstance(valor_aluguel, str):
        valor_float = float(valor_aluguel.replace('.', '').replace(',', '.'))
    else:
        valor_float = valor_aluguel

    valor_por_extenso = num2words(valor_float, lang='pt_BR', to='currency')
    vigencia = relativedelta(contrato_aluguel.data_fim, contrato_aluguel.data_inicio)

    return {
        "nome_inquilino": inquilino.nome,
        "cpf_inquilino": inquilino.cpf,
        "rg_inquilino": f'{inquilino.rg}/{inquilino.orgao_emissor.upper()}',
        "status_civil_inquilino": inquilino.estado_civil,
        "profissao_ocupacao_inquilino": inquilino.profissao_ocupacao,
        "data_nascimento_inquilino": inquilino.data_nascimento,
        "email_inquilino": inquilino.email,
        "telefone_inquilino": inquilino.telefone,
        "nome_pai_inquilino": inquilino.nome_pai,
        "nome_mae_inquilino": inquilino.nome_mae,

        "endereco_imovel": imovel.endereco,
        "tipo_imovel": imovel.tipo_imovel.capitalize(),

        "nome_proprietario": proprietario.nome,
        "cpf_proprietario": proprietario.cpf,
        "rg_proprietario": f'{proprietario.rg}/{proprietario.orgao_emissor.upper()}',
        "status_civil_proprietario": proprietario.estado_civil,
        "profissao_ocupacao_proprietario": proprietario.profissao_ocupacao,

        "data_inicio_contrato": contrato_aluguel.data_inicio,
        "data_fim_contrato": contrato_aluguel.data_fim,
        "periodo_vigencia_contrato": f"{vigencia.years} ano(s), {vigencia.months} mês(es) e {vigencia.days} dia(s)",
        "valor_aluguel": valor_formatado,
        "valor_aluguel_extenso": str(valor_por_extenso),
        "dia_vencimento": contrato_aluguel.dia_vencimento,
        "data_assinatura": data_assinatura_contrato
    }
