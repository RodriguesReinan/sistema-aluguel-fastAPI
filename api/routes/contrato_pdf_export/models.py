from api.contrib.models import BaseModel
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class ContratoModeloPdfModel(BaseModel):
    __tablename__ = "contratos_modelo_pdf"

    id_pk: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(50), nullable=False)
    conteudo_html: Mapped[str] = mapped_column(Text, nullable=False)  # HTML com placeholders
