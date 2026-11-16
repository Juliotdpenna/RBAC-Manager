from utils import configuracao


def test_docs_desativadas_por_padrao(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)

    resultado = configuracao.configuracao_docs()

    assert resultado["docs_url"] is None
    assert resultado["openapi_url"] is None


def test_docs_ativas_em_desenvolvimento(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")

    assert configuracao.configuracao_docs() == {}


def test_origens_cors_vem_do_ambiente(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "https://a.com, https://b.com")

    assert configuracao.obter_origens_permitidas() == [
        "https://a.com",
        "https://b.com",
    ]
