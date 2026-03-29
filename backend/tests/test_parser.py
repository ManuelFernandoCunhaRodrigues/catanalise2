from services.parser import extract_fields


def test_extract_fields_with_multiline_description_and_labels() -> None:
    text = """
    Nome do profissional: Maria Oliveira
    Numero ART: 987654321
    Contratante: Construtora Horizonte
    Data de inicio: 15/02/2023
    Data de fim: 30/04/2023
    Descricao dos servicos:
    Execucao de drenagem profunda, pavimentacao e acompanhamento tecnico da obra.
    """

    result = extract_fields(text)

    assert result["nome_profissional"] == "Maria Oliveira"
    assert result["numero_art"] == "987654321"
    assert result["contratante"] == "Construtora Horizonte"
    assert result["descricao_servico"] is not None
    assert "drenagem" in result["descricao_servico"].lower()
