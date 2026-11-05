from fastapi import FastAPI
from .database import Base, engine
from .routes.movimentacoes import router as movimentacoes_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Controle Financeiro",
    description="API para gerenciamento de receitas e despesas",
    version="1.0.0"
)


app.include_router(movimentacoes_router)


@app.get("/")
def inicio():
    return {"mensagem": "API Controle Financeiro funcionando!"}


@app.get("/health")
def health():
    return {"status": "ok"}