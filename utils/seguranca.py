
from argon2 import PasswordHasher
from argon2.exceptions import (
    VerifyMismatchError,
    VerificationError,
    InvalidHashError,
)

hasher = PasswordHasher()


def gerar_hash_senha(senha: str) -> str:
    if not senha:
        raise ValueError("A senha não pode ser vazia.")

    return hasher.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return hasher.verify(senha_hash, senha)

    except (
        VerifyMismatchError,
        VerificationError,
        InvalidHashError,
    ):
        return False


HASH_FALSO = hasher.hash("senha-falsa-para-igualar-o-tempo")


def verificar_senha_falsa(senha: str) -> None:
    """Gasta o mesmo tempo de uma verificação real (evita enumeração por tempo)."""
    verificar_senha(senha, HASH_FALSO)