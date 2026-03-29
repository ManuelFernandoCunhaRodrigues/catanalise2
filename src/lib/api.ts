export interface ExtractedData {
  nome_profissional?: string | null;
  numero_art?: string | null;
  data_inicio?: string | null;
  data_fim?: string | null;
  data_execucao?: string | null;
  descricao_servico?: string | null;
  contratante?: string | null;
}

export interface ValidationResponse {
  valid: boolean;
  erros: string[];
  alertas: string[];
  inconsistencias: string[];
  score: number;
  nivel: string;
}

export interface ArtComparisonResponse {
  consistente: boolean;
  inconsistencias: string[];
  alertas: string[];
  resumo: string;
  art_encontrada?: ExtractedData | null;
}

export interface FraudResponse {
  fraude_detectada: boolean;
  nivel_risco: string;
  score_fraude?: number;
  fraudes: string[];
  alertas: string[];
  indicadores: string[];
  detalhes: string[];
  regras_avaliadas?: Array<{
    codigo: string;
    peso: number;
    acionada: boolean;
    explicacao: string;
  }>;
}

export interface ReliabilityScoreResponse {
  score: number;
  nivel: string;
  justificativa: string[];
  resumo: string;
}

export interface IntelligentFeedbackItem {
  tipo: string;
  mensagem: string;
  sugestao: string;
}

export interface IntelligentFeedbackResponse {
  feedback: IntelligentFeedbackItem[];
  resumo_geral: string;
  recomendacoes: string[];
  status: string;
}

export interface AnalyzeResponse {
  analysis_id?: number;
  filename: string;
  status: string;
  resultado: {
    mensagem: string;
    score: number;
    nivel: string;
  };
  texto_extraido?: string;
  dados_extraidos?: ExtractedData;
  validacao?: ValidationResponse;
  comparacao_art?: ArtComparisonResponse;
  fraude?: FraudResponse;
  score_confiabilidade?: ReliabilityScoreResponse;
  feedback_inteligente?: IntelligentFeedbackResponse;
  processamento?: {
    modo: string;
    arquivo_salvo: string;
    tempo_ms: number;
  };
}

export interface HistoryResponseItem {
  id: number;
  filename: string;
  score: number;
  nivel: string;
  data_criacao: string;
}

export interface HistoryDetailResponse extends HistoryResponseItem {
  erros: string[];
  alertas: string[];
  inconsistencias: string[];
  analysis?: AnalyzeResponse;
}

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/+$/, "");
const API_TOKEN = import.meta.env.VITE_API_TOKEN;

function buildHeaders(headers?: HeadersInit): HeadersInit {
  if (!API_TOKEN) {
    return headers ?? {};
  }

  return {
    ...(headers ?? {}),
    Authorization: `Bearer ${API_TOKEN}`,
  };
}

export async function analyzeCatDocument(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    headers: buildHeaders(),
    body: formData,
  });

  return handleJsonResponse<AnalyzeResponse>(response);
}

export async function fetchHistory(): Promise<HistoryResponseItem[]> {
  const response = await fetch(`${API_BASE_URL}/history`, {
    headers: buildHeaders(),
  });
  return handleJsonResponse<HistoryResponseItem[]>(response);
}

export async function fetchHistoryById(analysisId: number): Promise<HistoryDetailResponse> {
  const response = await fetch(`${API_BASE_URL}/history/${analysisId}`, {
    headers: buildHeaders(),
  });
  return handleJsonResponse<HistoryDetailResponse>(response);
}

async function handleJsonResponse<T>(response: Response): Promise<T> {
  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const detail =
      typeof payload?.detail === "string"
        ? payload.detail
        : "Nao foi possivel concluir a requisicao com o backend.";
    throw new Error(detail);
  }

  return payload as T;
}
