from jinja2 import Template
from weasyprint import HTML
import io


def preencher_html(html_template: str, dados: dict) -> str:
    template = Template(html_template)
    return template.render(**dados)


def gerar_pdf_a_partir_do_html(html: str) -> bytes:
    pdf_io = io.BytesIO()
    HTML(string=html).write_pdf(pdf_io)
    return pdf_io.getvalue()
