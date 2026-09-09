from datetime import date
from pydantic import BaseModel


class MovimentacaoCreate(BaseModel):
    descricao: str
    valor: float
    tipo: str
    categoria: str
    data: date


class MovimentacaoResponse(MovimentacaoCreate):
    id: int

    class Config:
        from_attributes = True