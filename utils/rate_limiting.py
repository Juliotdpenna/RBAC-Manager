import time
from threading import Lock

JANELA_TEMPO = 60
LIMITE_POR_IP = 5
LIMITE_POR_MATRICULA = 10

tentativas_login = {}
lock = Lock()


def _chaves(ip, matricula):
    chaves = [("ip", ip)]

    if matricula:
        chaves.append(("matricula", matricula.strip().lower()))

    return chaves


def _limpar(agora):
    for chave in list(tentativas_login):
        recentes = [
            t for t in tentativas_login[chave]
            if agora - t < JANELA_TEMPO
        ]

        if recentes:
            tentativas_login[chave] = recentes
        else:
            del tentativas_login[chave]


def verificar_limite(ip, matricula=None):
    agora = time.monotonic()
    limites = {"ip": LIMITE_POR_IP, "matricula": LIMITE_POR_MATRICULA}

    with lock:
        _limpar(agora)

        for chave in _chaves(ip, matricula):
            if len(tentativas_login.get(chave, [])) >= limites[chave[0]]:
                return False

        return True


def registrar_tentativa_falha(ip, matricula=None):
    agora = time.monotonic()

    with lock:
        for chave in _chaves(ip, matricula):
            tentativas_login.setdefault(chave, []).append(agora)
