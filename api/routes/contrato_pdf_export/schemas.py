from pydantic import BaseModel


class ContratoBase(BaseModel):
    titulo: str
    conteudo_html: str


class ContratoCreate(ContratoBase):
    pass


class ContratoResponse(ContratoBase):
    id: str

    class Config:
        extra = 'forbid'
        from_attributes = True


class ContratoUpdate(BaseModel):
    conteudo_html: str
