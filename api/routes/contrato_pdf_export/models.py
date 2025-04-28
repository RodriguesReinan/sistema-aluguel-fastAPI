from api.contrib.models import BaseModel
from sqlalchemy import Integer, String, Text, CHAR
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import CHAR as MYSQL_CHAR


class ContratoModeloPdfModel(BaseModel):
    __tablename__ = "contratos_modelo_pdf"

    pk_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(50), nullable=False)
    conteudo_html: Mapped[str] = mapped_column(Text, nullable=False)  # HTML com placeholders
    tenant_id: Mapped[CHAR] = mapped_column(MYSQL_CHAR(36), nullable=False)
