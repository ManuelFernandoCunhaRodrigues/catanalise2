from io import BytesIO

from fastapi.testclient import TestClient

import main as backend_main


client = TestClient(backend_main.app)


def _auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}


def test_history_requires_authentication(monkeypatch) -> None:
    monkeypatch.setenv("API_AUTH_TOKEN", "test-token")
    response = client.get("/history")
    assert response.status_code == 401


def test_analyze_endpoint_returns_analysis_id(monkeypatch) -> None:
    monkeypatch.setenv("API_AUTH_TOKEN", "test-token")

    async def fake_process_file(_file) -> dict:
        return {
            "filename": "teste.pdf",
            "status": "processado",
            "resultado": {"mensagem": "ok", "score": 91, "nivel": "alto"},
            "dados_extraidos": {"numero_art": "123456789"},
            "validacao": {"valid": True, "erros": [], "alertas": [], "inconsistencias": [], "score": 100, "nivel": "alto"},
            "comparacao_art": {"consistente": True, "inconsistencias": [], "alertas": [], "resumo": "ok", "art_encontrada": None},
            "fraude": {"fraude_detectada": False, "nivel_risco": "baixo", "score_fraude": 0, "fraudes": [], "alertas": [], "indicadores": [], "detalhes": [], "regras_avaliadas": []},
            "score_confiabilidade": {"score": 91, "nivel": "alto", "justificativa": [], "resumo": "ok"},
            "feedback_inteligente": {"feedback": [], "resumo_geral": "ok", "recomendacoes": [], "status": "aprovado"},
            "_persistencia": {"score": 91, "nivel": "alto", "erros": [], "alertas": [], "inconsistencias": [], "analysis_payload": {"filename": "teste.pdf"}},
        }

    monkeypatch.setattr(backend_main, "process_file", fake_process_file)
    monkeypatch.setattr(backend_main, "save_analysis", lambda payload: 321)

    response = client.post(
        "/analyze",
        headers=_auth_headers(),
        files={"file": ("teste.pdf", BytesIO(b"%PDF-1.4 fake").read(), "application/pdf")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["analysis_id"] == 321
    assert payload["resultado"]["score"] == 91
