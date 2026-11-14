import pytest


@pytest.fixture(autouse=True)
def chave_jwt_de_teste(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "chave-de-teste-" + "x" * 40)