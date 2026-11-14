import pytest
from fastapi.testclient import TestClient

import api
import utils.autenticacao as autenticacao
from api import app
from models.permissao import Permissao
from models.usuario import Usuario
from utils.autenticacao import obter_usuario_atual
from models.role import Role

client = TestClient(app)


@pytest.fixture
def admin_simulado(monkeypatch):
    admin = Usuario(7, "Admin", "ADM", "TI", "Admin", True, None)
    admin.pode_acessar = lambda permissao: True

    nomes = ["DESATIVAR_USUARIOS", "GERENCIAR_PERMISSOES", "GERENCIAR_ROLES"]
    permissoes = [
        Permissao(i + 1, nome, "descricao", True)
        for i, nome in enumerate(nomes)
    ]

    app.dependency_overrides[obter_usuario_atual] = lambda: admin
    monkeypatch.setattr(autenticacao, "consultar_permissoes", lambda: permissoes)
    monkeypatch.setattr(api, "consultar_permissoes", lambda: permissoes)

    yield admin

    app.dependency_overrides.clear()


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