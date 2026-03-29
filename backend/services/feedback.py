from typing import Any, Dict, List


def generate_feedback(validation_data: dict) -> dict:
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
        if "campo obrigatorio ausente" in lowered:
            feedback.append({"tipo": "erro", "mensagem": "Um campo obrigatorio nao foi preenchido.", "sugestao": "Revise o formulario e preencha todos os campos obrigatorios antes de enviar."})
        elif "data de fim anterior" in lowered:
            feedback.append({"tipo": "erro", "mensagem": "A data de fim esta anterior a data de inicio.", "sugestao": "Verifique e corrija o periodo de execucao da obra."})
        elif "data de fim ausente" in lowered:
            feedback.append({"tipo": "erro", "mensagem": "Existe data de inicio informada, mas a data final esta ausente.", "sugestao": "Informe a data de fim para completar corretamente o periodo executado."})
        elif "art informada sem descricao" in lowered:
            feedback.append({"tipo": "erro", "mensagem": "A ART foi informada, mas a atividade executada nao foi descrita.", "sugestao": "Descreva o servico realizado e vincule a descricao a ART informada."})
        elif "numero art invalido" in lowered:
            feedback.append({"tipo": "erro", "mensagem": "O numero da ART esta em formato invalido.", "sugestao": "Use apenas numeros e confirme a numeracao no documento original."})
        elif "invalida" in lowered and "data" in lowered:
            feedback.append({"tipo": "erro", "mensagem": "Uma das datas informadas nao esta no formato esperado.", "sugestao": "Use o formato DD/MM/AAAA e confira se o dia, mes e ano estao corretos."})
        else:
            feedback.append({"tipo": "erro", "mensagem": error, "sugestao": "Corrija esse item antes de submeter novamente o documento."})
    return _dedupe_feedback(feedback)


def generate_alert_feedback(alerts: List[str]) -> List[dict]:
    feedback: List[dict] = []
    for alert in alerts:
        lowered = alert.lower()
        if "descricao generica" in lowered:
            feedback.append({"tipo": "alerta", "mensagem": "Sua descricao esta muito vaga para uma boa analise.", "sugestao": "Adicione detalhes tecnicos da atividade executada, materiais, escopo ou metodo utilizado."})
        elif "descricao muito curta" in lowered or "texto muito curto" in lowered:
            feedback.append({"tipo": "alerta", "mensagem": "A descricao do servico esta curta demais.", "sugestao": "Inclua mais contexto sobre o que foi executado para aumentar a confiabilidade do documento."})
        elif "nome profissional incompleto" in lowered:
            feedback.append({"tipo": "alerta", "mensagem": "O nome do profissional parece incompleto.", "sugestao": "Informe nome e sobrenome completos para evitar duvidas na identificacao."})
        elif "numero art suspeito" in lowered:
            feedback.append({"tipo": "alerta", "mensagem": "O numero da ART parece curto ou incomum.", "sugestao": "Revise a ART informada e confirme se todos os digitos foram preenchidos."})
        elif "periodo de execucao muito curto" in lowered or "duracao muito curta" in lowered:
            feedback.append({"tipo": "alerta", "mensagem": "O periodo de execucao informado e muito curto.", "sugestao": "Confira se as datas representam corretamente a duracao real da atividade."})
        elif "ausencia de detalhes tecnicos" in lowered:
            feedback.append({"tipo": "alerta", "mensagem": "Faltam detalhes tecnicos na descricao do servico.", "sugestao": "Inclua informacoes como tipo de obra, escopo, metodos, materiais ou responsabilidade tecnica."})
        else:
            feedback.append({"tipo": "alerta", "mensagem": alert, "sugestao": "Revise esse ponto para melhorar a qualidade do documento."})
    return _dedupe_feedback(feedback)


def generate_inconsistency_feedback(inconsistencies: List[str]) -> List[dict]:
    feedback: List[dict] = []
    for inconsistency in inconsistencies:
        lowered = inconsistency.lower()
        if "divergencia" in lowered and "datas" in lowered:
            feedback.append({"tipo": "inconsistencia", "mensagem": "As datas informadas apresentam conflito entre si.", "sugestao": "Verifique se os periodos lancados estao corretos e coerentes com os demais dados."})
        elif "data de inicio no futuro" in lowered:
            feedback.append({"tipo": "inconsistencia", "mensagem": "A data de inicio esta no futuro.", "sugestao": "Confirme se a atividade ja ocorreu ou ajuste a data informada."})
        elif "data de fim no futuro" in lowered:
            feedback.append({"tipo": "inconsistencia", "mensagem": "A data de fim esta no futuro.", "sugestao": "Revise a data final e confirme se ela corresponde ao encerramento real da execucao."})
        elif "data de fim anterior" in lowered:
            feedback.append({"tipo": "inconsistencia", "mensagem": "O periodo informado esta inconsistente.", "sugestao": "Ajuste a ordem das datas para que a execucao termine apos o inicio."})
        else:
            feedback.append({"tipo": "inconsistencia", "mensagem": inconsistency, "sugestao": "Revise os dados relacionados para eliminar a divergencia identificada."})
    return _dedupe_feedback(feedback)


def generate_summary(data: dict) -> str:
    if data["fraudes"]:
        return "Seu documento apresenta sinais graves de risco e deve ser corrigido antes de seguir para analise. Revise os dados criticos e confirme as informacoes com a documentacao de origem."
    if data["erros"] or data["inconsistencias"]:
        return "Seu documento possui erros e inconsistencias que precisam ser corrigidos antes da aprovacao. Recomendamos revisar os campos obrigatorios, datas e informacoes conflitantes."
    if data["alertas"]:
        return "Seu documento pode seguir, mas ha pontos que merecem melhoria para aumentar a clareza e a confiabilidade da analise."
    return "Seu documento esta consistente e pronto para seguir no fluxo de analise."


def generate_recommendations(data: dict) -> List[str]:
    recommendations: List[str] = []
    if data["erros"]:
        recommendations.append("Revise e corrija todos os erros antes de tentar submeter novamente.")
        if any("campo obrigatorio" in item.lower() for item in data["erros"]):
            recommendations.append("Preencha todos os campos obrigatorios do documento.")
        if any("data" in item.lower() for item in data["erros"]):
            recommendations.append("Confira o periodo de execucao e ajuste as datas informadas.")
    if data["inconsistencias"]:
        recommendations.append("Verifique os dados conflitantes para alinhar datas e informacoes relacionadas.")
    if data["alertas"]:
        if any("descricao" in item.lower() for item in data["alertas"]):
            recommendations.append("Detalhe melhor a descricao do servico com informacoes tecnicas.")
        recommendations.append("Revise os alertas para aumentar a qualidade e a clareza do documento.")
    if data["fraudes"]:
        recommendations.insert(0, "Interrompa a submissao e valide o documento com a base original antes de prosseguir.")
    if not recommendations:
        recommendations.append("Nenhuma acao corretiva e necessaria no momento.")
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
        if "divergencia entre cat e art" in lowered:
            feedback.append({"tipo": "fraude", "mensagem": "Os dados da CAT nao batem com os dados da ART comparada.", "sugestao": "Compare os dois documentos e corrija as informacoes divergentes antes de reenviar."})
        elif "combinacao de alto risco" in lowered:
            feedback.append({"tipo": "fraude", "mensagem": "Foi identificada uma combinacao de sinais que eleva muito o risco do documento.", "sugestao": "Revalide a ART, as datas e a descricao com a documentacao original antes de prosseguir."})
        elif "campos criticos incompletos" in lowered:
            feedback.append({"tipo": "fraude", "mensagem": "Faltam dados essenciais para validar a autenticidade do documento.", "sugestao": "Complete os campos criticos e confirme as informacoes com a fonte oficial."})
        elif "numero art invalido" in lowered:
            feedback.append({"tipo": "fraude", "mensagem": "O numero da ART contem sinais de irregularidade.", "sugestao": "Confira a ART original e informe apenas a numeracao correta, sem caracteres extras."})
        else:
            feedback.append({"tipo": "fraude", "mensagem": fraud, "sugestao": "Interrompa o envio e revise esse ponto diretamente na documentacao de origem."})
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
