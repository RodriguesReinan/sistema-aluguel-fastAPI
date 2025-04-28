# from datetime import datetime
# from api.contrib.models import BaseModel
# from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, Enum
# from sqlalchemy.orm import Mapped, mapped_column, relationship
#
#
# class CorretorModel(BaseModel):
#     __tablename__ = 'corretores'
#
#     pk_id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     nome: Mapped[str] = mapped_column(String(50), nullable=False)
#     telefone: Mapped[str] = mapped_column(String(20), nullable=False)
#     email: Mapped[str] = mapped_column(String(100), nullable=False)