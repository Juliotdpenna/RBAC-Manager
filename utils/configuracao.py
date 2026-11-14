import os

from dotenv import load_dotenv

load_dotenv()

ORIGENS_PADRAO = "http://localhost:5173,http://127.0.0.1:5173"


def em_desenvolvimento() -> bool:
    return os.getenv("APP_ENV", "production").lower() == "development"


def obter_origens_permitidas() -> list[str]:
    bruto = os.getenv("CORS_ORIGINS", ORIGENS_PADRAO)

    return [origem.strip() for origem in bruto.split(",") if origem.strip()]


def configuracao_docs() -> dict:
    if em_desenvolvimento():
        return {}

    return {"docs_url": None, "redoc_url": None, "openapi_url": None}
