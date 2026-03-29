from typing import Any, Dict, List


def generate_feedback(validation_data: dict) -> dict:
    """
    Assistente explicável para orientar a correção da CAT antes da submissão.
    """
    normalized = _normalize_input(validation_data)

    feedback_items: List[dict] = []
    feedback_items.extend(generate_error_feedback(normalized["erros"]))
    feedback_items.extend(generate_inconsistency_feedback(normalized["inconsistencias"]))
    feedback_items.extend(generate_alert_feedback(normalized["alertas"]))
    feedback_items.extend(_generate_fraud_feedback(normalized["fraudes"]))

    return {
        "feedback": feedback_items,
        "resumo_geral": generate_summary(normalized),
        "recomendacoes": generate_recommendations(normalized),
        "status": define_status(normalized),
    }


def generate_error_feedback(errors: List[str]) -> List[dict]:
    feedback: List[dict] = []

    for error in errors:
        lowered = error.lower()
        if "campo obrigatório ausente" in lowered:
            feedback.append(
                {
                    "tipo": "erro",
                    "mensagem": "Um campo obrigatório não foi preenchido.",
                    "sugestao": "Revise o formulário e preencha todos os campos obrigatórios antes de enviar.",
                }
            )
        elif "data de fim anterior" in lowered:
            feedback.append(
                {
                    "tipo": "erro",
                    "mensagem": "A data de fim está anterior à data de início.",
                    "sugestao": "Verifique e corrija o período de execução da obra.",
                }
            )
        elif "data de fim ausente" in lowered:
            feedback.append(
                {
                    "tipo": "erro",
                    "mensagem": "Existe data de início informada, mas a data final está ausente.",
                    "sugestao": "Informe a data de fim para completar corretamente o período executado.",
                }
            )
        elif "art informada sem descrição" in lowered:
            feedback.append(
                {
                    "tipo": "erro",
                    "mensagem": "A ART foi informada, mas a atividade executada não foi descrita.",
                    "sugestao": "Descreva o serviço realizado e vincule a descrição à ART informada.",
                }
            )
        elif "número art inválido" in lowered:
            feedback.append(
                {
                    "tipo": "erro",
                    "mensagem": "O número da ART está em formato inválido.",
                    "sugestao": "Use apenas números e confirme a numeração no documento original.",
                }
            )
        elif "inválida" in lowered and "data" in lowered:
            feedback.append(
                {
                    "tipo": "erro",
                    "mensagem": "Uma das datas informadas não está no formato esperado.",
                    "sugestao": "Use o formato DD/MM/AAAA e confira se o dia, mês e ano estão corretos.",
                }
            )
        else:
            feedback.append(
                {
                    "tipo": "erro",
                    "mensagem": error,
                    "sugestao": "Corrija esse item antes de submeter novamente o documento.",
                }
            )

    return _dedupe_feedback(feedback)


def generate_alert_feedback(alerts: List[str]) -> List[dict]:
    feedback: List[dict] = []

    for alert in alerts:
        lowered = alert.lower()
        if "descrição genérica" in lowered:
            feedback.append(
                {
                    "tipo": "alerta",
                    "mensagem": "Sua descrição está muito vaga para uma boa análise.",
                    "sugestao": "Adicione detalhes técnicos da atividade executada, materiais, escopo ou método utilizado.",
                }
            )
        elif "descrição muito curta" in lowered or "texto muito curto" in lowered:
            feedback.append(
                {
                    "tipo": "alerta",
                    "mensagem": "A descrição do serviço está curta demais.",
                    "sugestao": "Inclua mais contexto sobre o que foi executado para aumentar a confiabilidade do documento.",
                }
            )
        elif "nome profissional incompleto" in lowered:
            feedback.append(
                {
                    "tipo": "alerta",
                    "mensagem": "O nome do profissional parece incompleto.",
                    "sugestao": "Informe nome e sobrenome completos para evitar dúvidas na identificação.",
                }
            )
        elif "número art suspeito" in lowered:
            feedback.append(
                {
                    "tipo": "alerta",
                    "mensagem": "O número da ART parece curto ou incomum.",
                    "sugestao": "Revise a ART informada e confirme se todos os dígitos foram preenchidos.",
                }
            )
        elif "período de execução muito curto" in lowered or "duração muito curta" in lowered:
            feedback.append(
                {
                    "tipo": "alerta",
                    "mensagem": "O período de execução informado é muito curto.",
                    "sugestao": "Confira se as datas representam corretamente a duração real da atividade.",
                }
            )
        elif "ausência de detalhes técnicos" in lowered:
            feedback.append(
                {
                    "tipo": "alerta",
                    "mensagem": "Faltam detalhes técnicos na descrição do serviço.",
                    "sugestao": "Inclua informações como tipo de obra, escopo, métodos, materiais ou responsabilidade técnica.",
                }
            )
        else:
            feedback.append(
                {
                    "tipo": "alerta",
                    "mensagem": alert,
                    "sugestao": "Revise esse ponto para melhorar a qualidade do documento.",
                }
            )

    return _dedupe_feedback(feedback)


def generate_inconsistency_feedback(inconsistencies: List[str]) -> List[dict]:
    feedback: List[dict] = []

    for inconsistency in inconsistencies:
        lowered = inconsistency.lower()
        if "divergência" in lowered and "datas" in lowered:
            feedback.append(
                {
                    "tipo": "inconsistencia",
                    "mensagem": "As datas informadas apresentam conflito entre si.",
                    "sugestao": "Verifique se os períodos lançados estão corretos e coerentes com os demais dados.",
                }
            )
        elif "data de início no futuro" in lowered:
            feedback.append(
                {
                    "tipo": "inconsistencia",
                    "mensagem": "A data de início está no futuro.",
                    "sugestao": "Confirme se a atividade já ocorreu ou ajuste a data informada.",
                }
            )
        elif "data de fim no futuro" in lowered:
            feedback.append(
                {
                    "tipo": "inconsistencia",
                    "mensagem": "A data de fim está no futuro.",
                    "sugestao": "Revise a data final e confirme se ela corresponde ao encerramento real da execução.",
                }
            )
        elif "data de fim anterior" in lowered:
            feedback.append(
                {
                    "tipo": "inconsistencia",
                    "mensagem": "O período informado está inconsistente.",
                    "sugestao": "Ajuste a ordem das datas para que a execução termine após o início.",
                }
            )
        else:
            feedback.append(
                {
                    "tipo": "inconsistencia",
                    "mensagem": inconsistency,
                    "sugestao": "Revise os dados relacionados para eliminar a divergência identificada.",
                }
            )

    return _dedupe_feedback(feedback)


def generate_summary(data: dict) -> str:
    if data["fraudes"]:
        return (
            "Seu documento apresenta sinais graves de risco e deve ser corrigido antes de seguir para análise. "
            "Revise os dados críticos e confirme as informações com a documentação de origem."
        )

    if data["erros"] or data["inconsistencias"]:
        return (
            "Seu documento possui erros e inconsistências que precisam ser corrigidos antes da aprovação. "
            "Recomendamos revisar os campos obrigatórios, datas e informações conflitantes."
        )

    if data["alertas"]:
        return (
            "Seu documento pode seguir, mas há pontos que merecem melhoria para aumentar a clareza e a confiabilidade da análise."
        )

    return "Seu documento está consistente e pronto para seguir no fluxo de análise."


def generate_recommendations(data: dict) -> List[str]:
    recommendations: List[str] = []

    if data["erros"]:
        recommendations.append("Revise e corrija todos os erros antes de tentar submeter novamente.")
        if any("campo obrigatório" in item.lower() for item in data["erros"]):
            recommendations.append("Preencha todos os campos obrigatórios do documento.")
        if any("data" in item.lower() for item in data["erros"]):
            recommendations.append("Confira o período de execução e ajuste as datas informadas.")

    if data["inconsistencias"]:
        recommendations.append("Verifique os dados conflitantes para alinhar datas e informações relacionadas.")

    if data["alertas"]:
        if any("descrição" in item.lower() for item in data["alertas"]):
            recommendations.append("Detalhe melhor a descrição do serviço com informações técnicas.")
        recommendations.append("Revise os alertas para aumentar a qualidade e a clareza do documento.")

    if data["fraudes"]:
        recommendations.insert(0, "Interrompa a submissão e valide o documento com a base original antes de prosseguir.")

    if not recommendations:
        recommendations.append("Nenhuma ação corretiva é necessária no momento.")

    return _dedupe_strings(recommendations)


def define_status(data: dict) -> str:
    if data["fraudes"]:
        return "reprovado"
    if data["erros"] or data["inconsistencias"]:
        return "revisar"
    if data["alertas"]:
        return "aprovado com ressalvas"
    return "aprovado"


def _generate_fraud_feedback(frauds: List[str]) -> List[dict]:
    feedback: List[dict] = []

    for fraud in frauds:
        lowered = fraud.lower()
        if "divergência entre cat e art" in lowered:
            feedback.append(
                {
                    "tipo": "fraude",
                    "mensagem": "Os dados da CAT não batem com os dados da ART comparada.",
                    "sugestao": "Compare os dois documentos e corrija as informações divergentes antes de reenviar.",
                }
            )
        elif "combinação de alto risco" in lowered:
            feedback.append(
                {
                    "tipo": "fraude",
                    "mensagem": "Foi identificada uma combinação de sinais que eleva muito o risco do documento.",
                    "sugestao": "Revalide a ART, as datas e a descrição com a documentação original antes de prosseguir.",
                }
            )
        elif "campos críticos incompletos" in lowered:
            feedback.append(
                {
                    "tipo": "fraude",
                    "mensagem": "Faltam dados essenciais para validar a autenticidade do documento.",
                    "sugestao": "Complete os campos críticos e confirme as informações com a fonte oficial.",
                }
            )
        elif "número art inválido" in lowered:
            feedback.append(
                {
                    "tipo": "fraude",
                    "mensagem": "O número da ART contém sinais de irregularidade.",
                    "sugestao": "Confira a ART original e informe apenas a numeração correta, sem caracteres extras.",
                }
            )
        else:
            feedback.append(
                {
                    "tipo": "fraude",
                    "mensagem": fraud,
                    "sugestao": "Interrompa o envio e revise esse ponto diretamente na documentação de origem.",
                }
            )

    return _dedupe_feedback(feedback)


def _normalize_input(data: Dict[str, Any]) -> Dict[str, List[str]]:
    return {
        "erros": _ensure_list(data.get("erros")),
        "alertas": _ensure_list(data.get("alertas")),
        "inconsistencias": _ensure_list(data.get("inconsistencias")),
        "fraudes": _ensure_list(data.get("fraudes")),
    }


def _ensure_list(value: Any) -> List[str]:
    if not value:
        return []
    return [str(item) for item in value]


def _dedupe_feedback(items: List[dict]) -> List[dict]:
    seen = set()
    result: List[dict] = []
    for item in items:
        key = (item["tipo"], item["mensagem"], item["sugestao"])
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _dedupe_strings(items: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
