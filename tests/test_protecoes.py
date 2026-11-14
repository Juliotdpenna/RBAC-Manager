import pytest
from fastapi.testclient import TestClient

import api
import utils.autenticacao as autenticacao
from api import app
from models.permissao import Permissao
from models.usuario import Usuario
from utils.autenticacao import obter_usuario_atual
from models.role import Role
from models.grupo import Grupo

client = TestClient(app)


@pytest.fixture
def admin_simulado(monkeypatch):
    admin = Usuario(7, "Admin", "ADM", "TI", "Admin", True, None)
    admin.pode_acessar = lambda permissao: True

    nomes = ["DESATIVAR_USUARIOS", "GERENCIAR_PERMISSOES", "GERENCIAR_ROLES", "GERENCIAR_GRUPOS"]
    permissoes = [
        Permissao(i + 1, nome, "descricao", True)
        for i, nome in enumerate(nomes)
    ]

    app.dependency_overrides[obter_usuario_atual] = lambda: admin
    monkeypatch.setattr(autenticacao, "consultar_permissoes", lambda: permissoes)
    monkeypatch.setattr(api, "consultar_permissoes", lambda: permissoes)

    yield admin

    app.dependency_overrides.clear()


def test_nao_adiciona_usuario_a_grupo_com_permissoes_que_nao_possui(
    admin_simulado, monkeypatch
):
    admin_simulado.pode_acessar = (
        lambda permissao: permissao.nome == "GERENCIAR_GRUPOS"
    )
    role = Role(5, "ROLE_PODEROSA", "descricao", True)
    role.permissoes = [Permissao(60, "VISUALIZAR_CRM", "descricao", True)]
    grupo = Grupo(3, "Grupo", "descricao", True)
    grupo.roles.append(role)
    alvo = Usuario(9, "Alvo", "M9", "TI", "Cargo", True, None)

    monkeypatch.setattr(api, "consultar_grupos", lambda: [grupo])
    monkeypatch.setattr(api, "consultar_usuarios", lambda: [alvo])

    resposta = client.post("/grupos/3/usuarios/9")

    assert resposta.status_code == 403


def test_nao_permite_desativar_a_propria_conta(admin_simulado):
    resposta = client.delete("/usuarios/7")

    assert resposta.status_code == 400


def test_nao_permite_desativar_permissao_protegida(admin_simulado, monkeypatch):
    protegida = Permissao(99, "GERENCIAR_PERMISSOES", "descricao", True)
    monkeypatch.setattr(api, "consultar_permissoes", lambda: [protegida])

    resposta = client.delete("/permissoes/99")

    assert resposta.status_code == 409

def test_nao_permite_desativar_role_protegida(admin_simulado, monkeypatch):
    role = Role(5, "ROLE_ADMINISTRADOR", "descricao", True)
    monkeypatch.setattr(api, "consultar_roles", lambda: [role])

    resposta = client.delete("/roles/5")

    assert resposta.status_code == 409

def test_nao_permite_remover_permissao_da_role_protegida(admin_simulado, monkeypatch):
    role = Role(5, "ROLE_ADMINISTRADOR", "descricao", True)
    monkeypatch.setattr(api, "consultar_roles", lambda: [role])

    resposta = client.delete("/roles/5/permissoes/1")

    assert resposta.status_code == 409

def test_nao_concede_permissao_que_nao_possui(admin_simulado, monkeypatch):
    admin_simulado.pode_acessar = (
        lambda permissao: permissao.nome == "GERENCIAR_ROLES"
    )
    alvo = Permissao(50, "VISUALIZAR_CRM", "descricao", True)
    monkeypatch.setattr(api, "consultar_permissoes", lambda: [alvo])

    resposta = client.post("/roles/5/permissoes/50")

    assert resposta.status_code == 403


def test_concede_permissao_que_possui(admin_simulado, monkeypatch):
    alvo = Permissao(50, "VISUALIZAR_CRM", "descricao", True)
    monkeypatch.setattr(api, "consultar_permissoes", lambda: [alvo])
    monkeypatch.setattr(
        api, "associar_permissao_role", lambda role_id, permissao_id: None
    )

    resposta = client.post("/roles/5/permissoes/50")

    assert resposta.status_code == 200

def test_rejeita_nome_de_role_gigante(admin_simulado):
    resposta = client.post(
        "/roles",
        json={"nome": "a" * 101, "descricao": "descricao"},
    )

    assert resposta.status_code == 422