from fastapi import FastAPI
from fastapi.responses import JSONResponse
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
    # BUG PROPOSITAL (v1.1.0): simula uma versao quebrada para testar o rollback.
    return JSONResponse(status_code=500, content={"status": "erro"})