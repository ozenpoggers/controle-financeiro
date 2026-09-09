import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base
from app.routes.movimentacoes import obter_banco


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_financeiro.db"

engine_teste = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionTeste = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_teste
)


def obter_banco_teste():
    banco = SessionTeste()
    try:
        yield banco
    finally:
        banco.close()


app.dependency_overrides[obter_banco] = obter_banco_teste

client = TestClient(app)


@pytest.fixture(autouse=True)
def preparar_banco():
    Base.metadata.drop_all(bind=engine_teste)
    Base.metadata.create_all(bind=engine_teste)
    yield
    Base.metadata.drop_all(bind=engine_teste)


def test_inicio():
    resposta = client.get("/")

    assert resposta.status_code == 200
    assert resposta.json()["mensagem"] == "API Controle Financeiro funcionando!"


def test_health():
    resposta = client.get("/health")

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "ok"


def test_listar_movimentacoes():
    resposta = client.get("/movimentacoes/")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)


def test_criar_receita():
    resposta = client.post(
        "/movimentacoes/",
        json={
            "descricao": "Salário",
            "valor": 3000,
            "tipo": "receita",
            "categoria": "Salário",
            "data": "2026-09-09"
        }
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["descricao"] == "Salário"
    assert dados["valor"] == 3000
    assert dados["tipo"] == "receita"


def test_criar_despesa():
    resposta = client.post(
        "/movimentacoes/",
        json={
            "descricao": "Aluguel",
            "valor": 1000,
            "tipo": "despesa",
            "categoria": "Moradia",
            "data": "2026-09-09"
        }
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["descricao"] == "Aluguel"
    assert dados["valor"] == 1000
    assert dados["tipo"] == "despesa"


def test_nao_deve_aceitar_valor_negativo():
    resposta = client.post(
        "/movimentacoes/",
        json={
            "descricao": "Teste",
            "valor": -100,
            "tipo": "despesa",
            "categoria": "Teste",
            "data": "2026-09-09"
        }
    )

    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "O valor deve ser maior que zero"


def test_nao_deve_aceitar_tipo_invalido():
    resposta = client.post(
        "/movimentacoes/",
        json={
            "descricao": "Teste",
            "valor": 100,
            "tipo": "investimento",
            "categoria": "Teste",
            "data": "2026-09-09"
        }
    )

    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "O tipo deve ser receita ou despesa"


def test_consultar_saldo():
    client.post(
        "/movimentacoes/",
        json={
            "descricao": "Salário",
            "valor": 3000,
            "tipo": "receita",
            "categoria": "Salário",
            "data": "2026-09-09"
        }
    )

    client.post(
        "/movimentacoes/",
        json={
            "descricao": "Aluguel",
            "valor": 1000,
            "tipo": "despesa",
            "categoria": "Moradia",
            "data": "2026-09-09"
        }
    )

    resposta = client.get("/movimentacoes/saldo")

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["total_receitas"] == 3000
    assert dados["total_despesas"] == 1000
    assert dados["saldo"] == 2000


def test_resumo_financeiro():
    client.post(
        "/movimentacoes/",
        json={
            "descricao": "Salário",
            "valor": 3000,
            "tipo": "receita",
            "categoria": "Salário",
            "data": "2026-09-09"
        }
    )

    resposta = client.get("/movimentacoes/resumo")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), dict)


def test_atualizar_movimentacao():
    criar = client.post(
        "/movimentacoes/",
        json={
            "descricao": "Despesa teste",
            "valor": 100,
            "tipo": "despesa",
            "categoria": "Teste",
            "data": "2026-09-09"
        }
    )

    movimentacao_id = criar.json()["id"]

    resposta = client.put(
        f"/movimentacoes/{movimentacao_id}",
        json={
            "descricao": "Despesa atualizada",
            "valor": 200,
            "tipo": "despesa",
            "categoria": "Teste",
            "data": "2026-09-09"
        }
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert dados["descricao"] == "Despesa atualizada"
    assert dados["valor"] == 200


def test_excluir_movimentacao():
    criar = client.post(
        "/movimentacoes/",
        json={
            "descricao": "Movimentação para excluir",
            "valor": 50,
            "tipo": "despesa",
            "categoria": "Teste",
            "data": "2026-09-09"
        }
    )

    movimentacao_id = criar.json()["id"]

    resposta = client.delete(
        f"/movimentacoes/{movimentacao_id}"
    )

    assert resposta.status_code == 200
    assert resposta.json()["mensagem"] == "Movimentação excluída com sucesso"