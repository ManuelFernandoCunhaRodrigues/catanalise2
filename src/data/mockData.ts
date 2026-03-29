export const mockExtractedData = {
  obra: {
    contrato: "CT-2024/0847",
    endereco: "Av. Paulista, 1578 - Bela Vista, São Paulo - SP, 01310-200",
    periodoInicio: "15/03/2023",
    periodoFim: "28/11/2023",
    prazoContratual: "8 meses",
    parcelasExecutadas: "100%",
  },
  contratante: {
    tipo: "PJ" as const,
    nome: "Prefeitura Municipal de São Paulo",
    documento: "46.395.000/0001-39",
  },
  contratada: {
    razaoSocial: "Construtora Alfa Engenharia Ltda.",
    cnpj: "12.345.678/0001-90",
  },
  responsaveis: [
    {
      nome: "Eng. Carlos Alberto Silva",
      titulo: "Engenheiro Civil",
      rnp: "2612345678",
      crea: "SP-123456/D",
    },
    {
      nome: "Eng. Maria Fernanda Costa",
      titulo: "Engenheira de Estruturas",
      rnp: "2698765432",
      crea: "SP-654321/D",
    },
  ],
  servicos: {
    descricao:
      "Execução de obras de pavimentação asfáltica, incluindo terraplenagem, drenagem superficial e sinalização viária em vias urbanas do município.",
    quantitativos: [
      { item: "Terraplenagem", unidade: "m³", quantidade: "12.500" },
      { item: "Pavimentação asfáltica (CBUQ)", unidade: "m²", quantidade: "45.000" },
      { item: "Meio-fio", unidade: "m", quantidade: "8.200" },
      { item: "Drenagem", unidade: "m", quantidade: "3.100" },
    ],
  },
  assinaturas: {
    representanteContratante: "João Pedro Mendes - Secretário de Obras",
    profissionalHabilitado: "Eng. Carlos Alberto Silva - CREA SP-123456/D",
  },
};

export const mockValidations = {
  aprovados: [
    "CPF/CNPJ do contratante válido",
    "CNPJ da contratada válido",
    "Datas de início e fim coerentes",
    "RNP presente para todos os responsáveis",
    "Registro CREA válido",
  ],
  erros: [
    "Descrição sem quantitativos detalhados para sinalização viária",
  ],
  alertas: [
    "Assinatura digital não detectada — verificar autenticidade",
    "Prazo contratual próximo ao limite para licitação simplificada",
  ],
};

export const mockScore = {
  geral: 82,
  completude: 90,
  consistencia: 78,
  confiabilidade: 80,
};

export const mockFeedback =
  "A CAT apresenta boa completude geral, com todos os campos obrigatórios preenchidos. No entanto, a descrição dos serviços não apresenta quantitativos suficientes para sinalização viária, o que pode comprometer a validação técnica em processos licitatórios. Recomenda-se detalhar os volumes e especificações executados nesse item. A assinatura digital não foi detectada — sugere-se digitalizar novamente com certificado ICP-Brasil.";

export const mockHistory = [
  { id: "1", nome: "CAT-2024-0847.pdf", data: "28/03/2026", score: 82, status: "Revisão" as const },
  { id: "2", nome: "CAT-2024-0512.pdf", data: "25/03/2026", score: 95, status: "Aprovado" as const },
  { id: "3", nome: "CAT-2024-0398.pdf", data: "22/03/2026", score: 45, status: "Reprovado" as const },
  { id: "4", nome: "CAT-2023-1205.pdf", data: "18/03/2026", score: 91, status: "Aprovado" as const },
  { id: "5", nome: "CAT-2023-1102.pdf", data: "15/03/2026", score: 67, status: "Revisão" as const },
  { id: "6", nome: "CAT-2023-0988.pdf", data: "10/03/2026", score: 88, status: "Aprovado" as const },
];

export const mockDashboard = {
  totalAnalisadas: 127,
  tempoMedio: "2.4s",
  taxaErro: 12.5,
  chartData: [
    { mes: "Out", aprovadas: 18, revisao: 5, reprovadas: 2 },
    { mes: "Nov", aprovadas: 22, revisao: 7, reprovadas: 3 },
    { mes: "Dez", aprovadas: 15, revisao: 4, reprovadas: 1 },
    { mes: "Jan", aprovadas: 20, revisao: 6, reprovadas: 2 },
    { mes: "Fev", aprovadas: 25, revisao: 3, reprovadas: 4 },
    { mes: "Mar", aprovadas: 19, revisao: 5, reprovadas: 1 },
  ],
};

export const demoScenario = {
  fileName: "CAT-DEMO-2026.pdf",
  extractedData: {
    nome_profissional: "Joao Silva",
    numero_art: "123456789",
    data_inicio: "15/03/2023",
    data_fim: "10/03/2023",
    descricao_servico: "obra",
    contratante: "Empresa X",
  },
  artData: {
    numero_art: "123456789",
    nome_profissional: "Joao Silva",
    data_inicio: "20/03/2023",
    data_fim: "30/03/2023",
  },
  validations: {
    erros: [
      "Data de fim anterior a data de inicio",
    ],
    alertas: [
      "Descricao generica",
    ],
    inconsistencias: [
      "Periodo informado na CAT e incompativel com a ART vinculada",
    ],
  },
  fraud: {
    fraude_detectada: true,
    nivel_risco: "alto",
    indicadores: [
      "Inconsistencia critica de datas",
      "Descricao generica",
      "Divergencia entre CAT e ART",
    ],
    detalhes: [
      "A data final e anterior a data inicial na CAT.",
      "A descricao e vaga demais para sustentar a atividade executada.",
      "O periodo da CAT comeca antes da ART encontrada para o mesmo numero.",
    ],
  },
  reliabilityScore: {
    score: 38,
    nivel: "baixo",
    justificativa: [
      "Erro critico reduz significativamente a confiabilidade: data inconsistente.",
      "Inconsistencia com a ART reduz a seguranca da analise.",
      "Descricao generica adiciona risco e baixa qualidade documental.",
    ],
    resumo:
      "Este documento apresenta inconsistencias e indicios de risco, resultando em confiabilidade baixa. Recomenda-se revisao antes da aprovacao.",
  },
  intelligentFeedback: {
    feedback: [
      {
        tipo: "erro",
        mensagem: "A data de fim esta anterior a data de inicio.",
        sugestao: "Verifique e corrija o periodo de execucao da obra.",
      },
      {
        tipo: "alerta",
        mensagem: "Sua descricao esta muito vaga para uma boa analise.",
        sugestao: "Adicione detalhes tecnicos da atividade executada.",
      },
      {
        tipo: "inconsistencia",
        mensagem: "Os dados da CAT nao estao compativeis com a ART encontrada.",
        sugestao: "Revise o periodo vinculado a ART e ajuste o documento antes da submissao.",
      },
    ],
    resumo_geral:
      "O documento precisa de revisao antes do envio final. O sistema identificou automaticamente conflito de datas, descricao insuficiente e divergencia com a ART.",
    recomendacoes: [
      "Corrigir o periodo de execucao da obra.",
      "Detalhar melhor a descricao do servico.",
      "Conferir a ART vinculada antes da aprovacao.",
    ],
    status: "reprovado" as const,
  },
  historyItem: {
    id: "demo-1",
    nome: "CAT-DEMO-2026.pdf",
    data: "29/03/2026",
    score: 38,
    status: "Reprovado" as const,
  },
};
