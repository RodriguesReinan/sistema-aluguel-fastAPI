from fastapi import APIRouter, status, HTTPException
from fastapi.responses import StreamingResponse
from api.routes.contrato_pdf_export.schemas import ContratoCreate, ContratoResponse, ContratoUpdate
from api.services import contrato_pdf_service
from api.contrib.dependecies import DatabaseDependency

from api.utils.pdf_generator import preencher_html, gerar_pdf_a_partir_do_html
import io

router = APIRouter()


@router.post("/",
             summary='Criar/Redigir um documento de contrato de aluguel para assinatura',
             status_code=status.HTTP_201_CREATED,
             response_model=ContratoResponse
             )
async def criar(contrato: ContratoCreate, db_session: DatabaseDependency):
    return await contrato_pdf_service.criar_contrato(db_session, contrato)


@router.get("/",
            summary='Listar todos os modelos de contratos redigidos',
            status_code=status.HTTP_200_OK,
            response_model=list[ContratoResponse]
            )
async def listar(db_session: DatabaseDependency):
    return await contrato_pdf_service.listar_contratos(db_session)


@router.get("/{contrato_id}",
            summary='Obter um modelo de contrato específico, através do id',
            status_code=status.HTTP_200_OK,
            response_model=ContratoResponse
            )
async def obter(contrato_id: str, db_session: DatabaseDependency):
    contrato = await contrato_pdf_service.obter_contrato(db_session, contrato_id)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    return contrato


@router.post("/{contrato_id}/preencher",
             summary='Montagem do HTML/PDF do contrato, que está interpolado com os nomes das '
                     'variáveis {{nome_inqulino}}',
             status_code=status.HTTP_201_CREATED
             )
async def preencher_contrato(contrato_id: str, contrato_aluguel_id: str, db_session: DatabaseDependency):
    print('contrato_aluguel_id: ', contrato_aluguel_id)
    contrato = await contrato_pdf_service.obter_contrato(db_session, contrato_id)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    # dados = contrato_pdf_service.montar_dados_contrato(contrato_id, db_session)   '217eb48f-5e17-4797-87e6-ff1bbc2a2e01', '93a9ae3a-4f34-4899-ac0d-4f7b436532f7',
    dados = await contrato_pdf_service.montar_dados_contrato(contrato_id, contrato_aluguel_id, db_session)
    html_preenchido = preencher_html(contrato.conteudo_html, dados)

    # Gera o PDF a partir do HTML
    pdf = gerar_pdf_a_partir_do_html(html_preenchido)

    # Retorna o PDF gerado
    return StreamingResponse(io.BytesIO(pdf), media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=contrato_{contrato_id}.pdf"
    })


@router.get("/{contrato_id}/html",
            summary='Monta o html para ser exibido no frontend',
            status_code=status.HTTP_200_OK
            )
async def obter_html_contrato(contrato_id: str, contrato_aluguel_id: str, db_session: DatabaseDependency):
    print('contrato_aluguel_id: ', contrato_aluguel_id)
    contrato = await contrato_pdf_service.obter_contrato(db_session, contrato_id)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    # dados = contrato_pdf_service.montar_dados_contrato(contrato_id, db_session)  # usa sua função que monta os dados
    dados = await contrato_pdf_service.montar_dados_contrato(contrato_id, contrato_aluguel_id, db_session)
    html_preenchido = preencher_html(contrato.conteudo_html, dados)

    return {"html": html_preenchido}


@router.put("/{contrato_id}",
            summary='Editar um modelo de contrato redigido e salvo no banco de dados',
            status_code=status.HTTP_200_OK
            )
async def editar_modelo_contrato(contrato_id: str, contrato: ContratoUpdate, db_session: DatabaseDependency):
    modelo = await contrato_pdf_service.atualizar_modelo_contrato(db_session, contrato_id, contrato)
    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo de contrato não encontrado")
    return {"mensagem": "Modelo atualizado com sucesso"}

