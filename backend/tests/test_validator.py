from services.validator import validate_fields


def test_validate_fields_flags_errors_and_alerts() -> None:
    payload = {
        "nome_profissional": "Joao",
        "numero_art": "12A45",
        "data_inicio": "15/03/2024",
        "data_fim": "14/03/2024",
        "descricao_servico": "obra",
        "contratante": "",
    }

    result = validate_fields(payload)

    assert result["valid"] is False
    assert any("Numero ART invalido" in error for error in result["erros"])
    assert any("Data de fim anterior" in item for item in result["inconsistencias"])
    assert any("Descricao muito generica" in item for item in result["alertas"])
