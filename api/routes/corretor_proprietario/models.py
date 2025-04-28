# from datetime import datetime
# from api.contrib.models import BaseModel
# from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, Enum
# from sqlalchemy.orm import Mapped, mapped_column, relationship
#
#
# class CorretorProprietarioModel(BaseModel):
#     __tablename__ = 'corretores_proprietarios'
#
#     pk_id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     corretor_id: Mapped[int] = mapped_column(ForeignKey('corretores.pk_id'), nullable=False)
#     proprietario_id: Mapped[int] = mapped_column(ForeignKey('proprietarios.pk_id'), nullable=False)
#     imovel_id: Mapped[int] = mapped_column(ForeignKey('imoveis.pk_id'), nullable=False)
