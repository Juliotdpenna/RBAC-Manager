import pytest
from utils import rate_limiting

@pytest.fixture(autouse=True)
def chave_jwt_de_teste(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "chave-de-teste-" + "x" * 40)


@pytest.fixture(autouse=True)
def limpar_rate_limit():
    rate_limiting.tentativas_login.clear()
    yield
    rate_limiting.tentativas_login.clear()
