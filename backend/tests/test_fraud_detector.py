from services.fraud_detector import detect_fraud


def test_detect_fraud_returns_weighted_rules() -> None:
    cat_data = {
        "nome_profissional": "Joao Silva",
        "numero_art": "12A45",
        "data_inicio": "15/03/2024",
        "data_fim": "14/03/2024",
        "descricao_servico": "obra obra obra",
        "contratante": "Empresa X",
    }
    art_data = {
        "nome_profissional": "Maria Souza",
        "numero_art": "123456789",
        "data_inicio": "16/03/2024",
        "data_fim": "20/03/2024",
    }

    result = detect_fraud(cat_data, art_data)

    assert result["fraude_detectada"] is True
    assert result["score_fraude"] >= 60
    assert any(rule["codigo"] == "invalid_art_number" for rule in result["regras_avaliadas"])
    assert "Divergencia entre CAT e ART" in result["fraudes"]
