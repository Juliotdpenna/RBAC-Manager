import os
from getpass import getpass

from dotenv import load_dotenv

from database.conexao import conectar
from utils.seguranca import gerar_hash_senha


load_dotenv()

ADMIN_MATRICULA = os.getenv("ADMIN_MATRICULA")


def redefinir_senha():
    if not ADMIN_MATRICULA:
        raise RuntimeError(
            "Configure ADMIN_MATRICULA no arquivo .env."
        )

    conexao = conectar()

    try:
        registro = conexao.execute(
            """
            SELECT id, status
            FROM usuarios
            WHERE matricula = ?
            """,
            (ADMIN_MATRICULA,),
        ).fetchone()

        if registro is None or not registro[1]:
            raise RuntimeError(
                "Administrador inexistente ou desativado."
            )

        senha = getpass("Digite a nova senha: ")
        confirmacao = getpass("Confirme a nova senha: ")

        if len(senha) < 12:
            raise ValueError(
                "A senha precisa ter pelo menos 12 caracteres."
            )
        if len(senha) > 128:
            raise ValueError(
                "A senha pode ter no máximo 128 caracteres."
            )
        if senha != confirmacao:
            raise ValueError("As senhas não coincidem.")

        senha_hash = gerar_hash_senha(senha)

        conexao.execute(
            """
            UPDATE usuarios
            SET senha_hash = ?
            WHERE id = ?
            """,
            (senha_hash, registro[0]),
        )

        conexao.commit()

        print("Senha redefinida com sucesso.")

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


if __name__ == "__main__":
    redefinir_senha()
