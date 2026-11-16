from types import SimpleNamespace

from utils import rate_limiting


def test_bloqueia_ip_apos_o_limite():
    for _ in range(rate_limiting.LIMITE_POR_IP):
        rate_limiting.registrar_tentativa_falha("1.1.1.1")

    assert rate_limiting.verificar_limite("1.1.1.1") is False
    assert rate_limiting.verificar_limite("2.2.2.2") is True


def test_bloqueia_matricula_mesmo_com_ips_diferentes():
    for i in range(rate_limiting.LIMITE_POR_MATRICULA):
        rate_limiting.registrar_tentativa_falha(f"10.0.0.{i}", "ABC123")

    assert rate_limiting.verificar_limite("99.9.9.9", "abc123") is False
    assert rate_limiting.verificar_limite("99.9.9.9", "outra") is True


def test_tentativas_expiram_apos_a_janela(monkeypatch):
    relogio = [1000.0]
    monkeypatch.setattr(
        rate_limiting,
        "time",
        SimpleNamespace(monotonic=lambda: relogio[0]),
    )

    for _ in range(rate_limiting.LIMITE_POR_IP):
        rate_limiting.registrar_tentativa_falha("1.1.1.1")

    assert rate_limiting.verificar_limite("1.1.1.1") is False

    relogio[0] += rate_limiting.JANELA_TEMPO + 1

    assert rate_limiting.verificar_limite("1.1.1.1") is True
