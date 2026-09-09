from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Movimentacao
from ..schemas import MovimentacaoCreate, MovimentacaoResponse

router = APIRouter(prefix="/movimentacoes", tags=["Movimentações"])


def obter_banco():
    banco = SessionLocal()
    try:
        yield banco
    finally:
        banco.close()


@router.post("/", response_model=MovimentacaoResponse)
def criar_movimentacao(
    movimentacao: MovimentacaoCreate,
    banco: Session = Depends(obter_banco)
):
    if movimentacao.valor <= 0:
        raise HTTPException(
            status_code=400,
            detail="O valor deve ser maior que zero"
        )

    if movimentacao.tipo not in ["receita", "despesa"]:
        raise HTTPException(
            status_code=400,
            detail="O tipo deve ser receita ou despesa"
        )

    nova_movimentacao = Movimentacao(
        descricao=movimentacao.descricao,
        valor=movimentacao.valor,
        tipo=movimentacao.tipo,
        categoria=movimentacao.categoria,
        data=movimentacao.data
    )

    banco.add(nova_movimentacao)
    banco.commit()
    banco.refresh(nova_movimentacao)

    return nova_movimentacao


@router.get("/", response_model=list[MovimentacaoResponse])
def listar_movimentacoes(
    banco: Session = Depends(obter_banco)
):
    return banco.query(Movimentacao).all()


@router.put("/{movimentacao_id}", response_model=MovimentacaoResponse)
def atualizar_movimentacao(
    movimentacao_id: int,
    dados: MovimentacaoCreate,
    banco: Session = Depends(obter_banco)
):
    movimentacao = banco.query(Movimentacao).filter(
        Movimentacao.id == movimentacao_id
    ).first()

    if not movimentacao:
        raise HTTPException(
            status_code=404,
            detail="Movimentação não encontrada"
        )

    if dados.valor <= 0:
        raise HTTPException(
            status_code=400,
            detail="O valor deve ser maior que zero"
        )

    if dados.tipo not in ["receita", "despesa"]:
        raise HTTPException(
            status_code=400,
            detail="O tipo deve ser receita ou despesa"
        )

    movimentacao.descricao = dados.descricao
    movimentacao.valor = dados.valor
    movimentacao.tipo = dados.tipo
    movimentacao.categoria = dados.categoria
    movimentacao.data = dados.data

    banco.commit()
    banco.refresh(movimentacao)

    return movimentacao

@router.delete("/{movimentacao_id}")
def excluir_movimentacao(
    movimentacao_id: int,
    banco: Session = Depends(obter_banco)
):
    movimentacao = banco.query(Movimentacao).filter(
        Movimentacao.id == movimentacao_id
    ).first()

    if not movimentacao:
        raise HTTPException(
            status_code=404,
            detail="Movimentação não encontrada"
        )

    banco.delete(movimentacao)
    banco.commit()

    return {"mensagem": "Movimentação excluída com sucesso"}

@router.get("/saldo")
def consultar_saldo(
    banco: Session = Depends(obter_banco)
):
    movimentacoes = banco.query(Movimentacao).all()

    receitas = sum(
        m.valor for m in movimentacoes
        if m.tipo == "receita"
    )

    despesas = sum(
        m.valor for m in movimentacoes
        if m.tipo == "despesa"
    )

    saldo = receitas - despesas

    return {
        "total_receitas": receitas,
        "total_despesas": despesas,
        "saldo": saldo
    }

@router.get("/resumo")
def resumo_financeiro(
    banco: Session = Depends(obter_banco)
):
    movimentacoes = banco.query(Movimentacao).all()

    resumo = {}

    for movimentacao in movimentacoes:
        categoria = movimentacao.categoria

        if categoria not in resumo:
            resumo[categoria] = {
                "receitas": 0,
                "despesas": 0
            }

        if movimentacao.tipo == "receita":
            resumo[categoria]["receitas"] += movimentacao.valor
        else:
            resumo[categoria]["despesas"] += movimentacao.valor

    return resumo