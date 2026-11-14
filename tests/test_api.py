from fastapi.testclient import TestClient
import api
from api import app


client = TestClient(app)


def test_rota_inicial():
    resposta = client.get("/")

    assert resposta.status_code == 200


def test_auth_me_sem_token():
    resposta = client.get("/auth/me")

    assert resposta.status_code == 401


def test_listar_usuarios_sem_token():
    resposta = client.get("/usuarios")

    assert resposta.status_code == 401


def test_login_com_credenciais_validas(monkeypatch):
    registro = (
    1,
    "12345",
    True,
    "hash-ficticio"
)

    monkeypatch.setattr(
        api,
        "consultar_usuario_login",
        lambda matricula: registro
    )

    monkeypatch.setattr(
        api,
        "verificar_senha",
        lambda senha, senha_hash: True
    )

    monkeypatch.setattr(
        api,
        "criar_access_token",
        lambda usuario_id: "token-de-teste"
    )

    resposta = client.post(
        "/auth/login",
        json={
            "matricula": "12345",
            "senha": "senha-ficticia"
        }
    )

    assert resposta.status_code == 200
    assert resposta.json()["access_token"] == "token-de-teste"
    assert resposta.json()["token_type"] == "bearer"


def test_login_com_senha_incorreta(monkeypatch):
    registro = (
        1,
        "12345",
        True,
        "hash-ficticio"
    )

    monkeypatch.setattr(
        api,
        "consultar_usuario_login",
        lambda matricula: registro
    )

    monkeypatch.setattr(
        api,
        "verificar_senha",
        lambda senha, senha_hash: False
    )

    resposta = client.post(
        "/auth/login",
        json={
            "matricula": "12345",
            "senha": "senha-incorreta"
        }
    )

    assert resposta.status_code == 401


def test_login_com_matricula_inexistente(monkeypatch):
    monkeypatch.setattr(
        api,
        "consultar_usuario_login",
        lambda matricula: None
    )

    resposta = client.post(
        "/auth/login",
        json={
            "matricula": "99999",
            "senha": "senha-ficticia"
        }
    )

    assert resposta.status_code == 401

def test_login_com_senha_gigante():
    resposta = client.post(
        "/auth/login",
        json={"matricula": "12345", "senha": "a" * 100_000},
    )

    assert resposta.status_code == 422


def test_login_usuario_inativo_executa_verificacao_falsa(monkeypatch):
    chamadas = []

    monkeypatch.setattr(
        api,
        "consultar_usuario_login",
        lambda matricula: (1, "12345", False, "hash-ficticio"),
    )
    monkeypatch.setattr(
        api, "verificar_senha_falsa", lambda senha: chamadas.append(senha)
    )

    resposta = client.post(
        "/auth/login",
        json={"matricula": "12345", "senha": "senha-ficticia"},
    )

    assert resposta.status_code == 401
    assert chamadas == ["senha-ficticia"]


def test_login_matricula_inexistente_executa_verificacao_falsa(monkeypatch):
    chamadas = []

    monkeypatch.setattr(api, "consultar_usuario_login", lambda matricula: None)
    monkeypatch.setattr(
        api, "verificar_senha_falsa", lambda senha: chamadas.append(senha)
    )

    resposta = client.post(
        "/auth/login",
        json={"matricula": "99999", "senha": "senha-ficticia"},
    )

    assert resposta.status_code == 401
    assert chamadas == ["senha-ficticia"]