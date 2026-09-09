from sqlalchemy import Column, Integer, String, Float, Date
from .database import Base


class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, nullable=False)
    valor = Column(Float, nullable=False)
    tipo = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    data = Column(Date, nullable=False)