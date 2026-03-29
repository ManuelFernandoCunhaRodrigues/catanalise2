import { useEffect, useMemo, useState, type ElementType } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  ArrowRightLeft,
  Brain,
  Building2,
  CheckCircle,
  Download,
  Edit,
  FileSearch,
  RefreshCw,
  ShieldAlert,
  User,
  XCircle,
} from "lucide-react";

import { fetchHistoryById, type AnalyzeResponse, type HistoryDetailResponse } from "@/lib/api";
import { getLastAnalysis, saveLastAnalysis } from "@/lib/analysis-store";
import { formatBackendDate, formatScoreLevel, getStatusFromScore } from "@/lib/analysis-utils";
import { ScoreBar } from "@/components/ScoreBar";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

function SectionHeader({ icon: Icon, title }: { icon: ElementType; title: string }) {
  return (
    <div className="mb-3 flex items-center gap-2">
      <Icon className="h-4 w-4 text-primary" />
      <h4 className="text-sm font-medium">{title}</h4>
    </div>
  );
}

function Field({ label, value }: { label: string; value?: string | number | null }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-sm">{value ?? "Nao informado"}</p>
    </div>
  );
}

function IssueList({
  title,
  icon: Icon,
  items,
  emptyText,
  tone,
}: {
  title: string;
  icon: ElementType;
  items: string[];
  emptyText: string;
  tone: "success" | "warning" | "error";
}) {
  const toneClass = {
    success: "text-success",
    warning: "text-warning",
    error: "text-destructive",
  }[tone];

  const visibleItems = items.length > 0 ? items : [emptyText];

  return (
    <Card className="shadow-sm">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-sm">
          <Icon className={`h-4 w-4 ${toneClass}`} />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {visibleItems.map((item) => (
          <div key={item} className="flex items-start gap-2 text-sm">
            <Icon className={`mt-0.5 h-3.5 w-3.5 shrink-0 ${toneClass}`} />
            <span>{item}</span>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

export default function Analise() {
  const location = useLocation();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(() => {
    const navigationState = location.state as { analysis?: AnalyzeResponse } | null;
    return navigationState?.analysis ?? getLastAnalysis();
  });
  const [analysisDetail, setAnalysisDetail] = useState<HistoryDetailResponse | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [isDetailLoading, setIsDetailLoading] = useState(false);

  useEffect(() => {
    const navigationState = location.state as { analysis?: AnalyzeResponse } | null;
    if (navigationState?.analysis) {
      setAnalysis(navigationState.analysis);
      saveLastAnalysis(navigationState.analysis);
    }
  }, [location.state]);

  useEffect(() => {
    if (!analysis?.analysis_id) {
      setAnalysisDetail(null);
      setDetailError(null);
      setIsDetailLoading(false);
      return;
    }

    let active = true;
    setDetailError(null);
    setIsDetailLoading(true);

    fetchHistoryById(analysis.analysis_id)
      .then((detail) => {
        if (!active) {
          return;
        }

        setAnalysisDetail(detail);
      })
      .catch((error) => {
        if (!active) {
          return;
        }

        setAnalysisDetail(null);
        setDetailError(error instanceof Error ? error.message : "Nao foi possivel carregar os detalhes da analise.");
      })
      .finally(() => {
        if (active) {
          setIsDetailLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [analysis?.analysis_id]);

  const fullAnalysis = useMemo(() => {
    if (analysisDetail?.analysis) {
      return {
        ...analysisDetail.analysis,
        analysis_id: analysisDetail.analysis.analysis_id ?? analysisDetail.id,
      };
    }
    return analysis;
  }, [analysis, analysisDetail]);

  const documentName = fullAnalysis?.filename ?? "Sem documento carregado";
  const finalScore = fullAnalysis?.score_confiabilidade?.score ?? fullAnalysis?.resultado.score ?? 0;
  const finalLevel = fullAnalysis?.score_confiabilidade?.nivel ?? fullAnalysis?.resultado.nivel;
  const status = getStatusFromScore(finalScore);
  const scoreColor = finalScore >= 80 ? "text-success" : finalScore >= 50 ? "text-warning" : "text-destructive";

  const combinedIssues = useMemo(() => {
    return {
      erros: analysisDetail?.erros ?? fullAnalysis?.validacao?.erros ?? [],
      alertas: dedupe([
        ...(fullAnalysis?.validacao?.alertas ?? []),
        ...(analysisDetail?.alertas ?? []),
      ]),
      inconsistencias: dedupe([
        ...(fullAnalysis?.validacao?.inconsistencias ?? []),
        ...(analysisDetail?.inconsistencias ?? []),
      ]),
    };
  }, [analysisDetail, fullAnalysis]);

  const approvedItems = useMemo(() => {
    if (!fullAnalysis) {
      return [];
    }

    if (combinedIssues.erros.length === 0 && combinedIssues.alertas.length === 0 && combinedIssues.inconsistencias.length === 0) {
      return ["Nenhum problema critico identificado nesta analise."];
    }

    return ["Documento processado e disponivel para auditoria detalhada."];
  }, [combinedIssues.alertas.length, combinedIssues.erros.length, combinedIssues.inconsistencias.length, fullAnalysis]);

  const reportDate = analysisDetail?.data_criacao ? formatBackendDate(analysisDetail.data_criacao) : null;
  const feedbackItems = fullAnalysis.feedback_inteligente?.feedback ?? [];
  const recommendations = fullAnalysis.feedback_inteligente?.recomendacoes ?? [];
  const scoreJustifications = fullAnalysis.score_confiabilidade?.justificativa ?? [];

  const handleDownloadReport = () => {
    if (!fullAnalysis) {
      return;
    }

    const reportPayload = {
      generated_at: new Date().toISOString(),
      analysis_id: fullAnalysis.analysis_id ?? analysisDetail?.id ?? null,
      analysis: fullAnalysis,
      history_summary: analysisDetail
        ? {
            id: analysisDetail.id,
            score: analysisDetail.score,
            nivel: analysisDetail.nivel,
            data_criacao: analysisDetail.data_criacao,
          }
        : null,
    };

    const blob = new Blob([JSON.stringify(reportPayload, null, 2)], { type: "application/json;charset=utf-8" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${sanitizeFilename(documentName.replace(/\.pdf$/i, "")) || "analise-cat"}-relatorio.json`;
    link.click();
    window.URL.revokeObjectURL(url);
  };

  if (!fullAnalysis) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-semibold">Resultado da Analise</h2>
          <p className="mt-1 text-sm text-muted-foreground">Nenhuma analise esta disponivel no momento.</p>
        </div>

        <Card className="max-w-2xl shadow-sm">
          <CardContent className="space-y-4 pt-6">
            <p className="text-sm text-muted-foreground">
              Envie uma CAT na tela de upload ou abra uma analise a partir do historico para ver os detalhes completos.
            </p>
            <div className="flex flex-wrap gap-2">
              <Button onClick={() => navigate("/upload")}>
                <Edit className="mr-1.5 h-3.5 w-3.5" />
                Fazer upload
              </Button>
              <Button variant="outline" onClick={() => navigate("/historico")}>
                <RefreshCw className="mr-1.5 h-3.5 w-3.5" />
                Ver historico
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Resultado da Analise</h2>
          <p className="mt-1 text-sm text-muted-foreground">{documentName}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" onClick={() => navigate("/upload")}>
            <Edit className="mr-1.5 h-3.5 w-3.5" />
            Novo upload
          </Button>
          <Button variant="outline" size="sm" onClick={() => navigate("/historico")}>
            <RefreshCw className="mr-1.5 h-3.5 w-3.5" />
            Ver historico
          </Button>
          <Button size="sm" onClick={handleDownloadReport}>
            <Download className="mr-1.5 h-3.5 w-3.5" />
            Baixar relatorio
          </Button>
        </div>
      </div>

      <Card className="shadow-sm">
        <CardContent className="flex flex-col gap-4 pt-6 md:flex-row md:items-center md:justify-between">
          <div className="space-y-2">
            <p className="text-sm font-medium">Resumo da API</p>
            <p className="text-sm text-muted-foreground">{fullAnalysis.resultado.mensagem}</p>
            <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
              {fullAnalysis.analysis_id && <span>ID da analise: {fullAnalysis.analysis_id}</span>}
              {reportDate && <span>Registrada em: {reportDate}</span>}
              {fullAnalysis.comparacao_art?.art_encontrada?.numero_art && (
                <span>ART relacionada: {fullAnalysis.comparacao_art.art_encontrada.numero_art}</span>
              )}
            </div>
            {detailError && <p className="text-xs text-destructive">{detailError}</p>}
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <StatusBadge status={status} />
            <span className={`text-2xl font-bold ${scoreColor}`}>{finalScore}</span>
            <span className="text-sm text-muted-foreground">{formatScoreLevel(finalLevel)}</span>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="extracao" className="space-y-4">
        <TabsList className="grid w-full max-w-3xl grid-cols-5">
          <TabsTrigger value="extracao">Extracao</TabsTrigger>
          <TabsTrigger value="validacao">Validacao</TabsTrigger>
          <TabsTrigger value="fraude">Fraude</TabsTrigger>
          <TabsTrigger value="score">Score</TabsTrigger>
          <TabsTrigger value="feedback">Feedback</TabsTrigger>
        </TabsList>

        <TabsContent value="extracao" className="space-y-4">
          <Card className="shadow-sm">
            <CardContent className="grid gap-4 pt-6 md:grid-cols-4">
              <Field label="Documento" value={documentName} />
              <Field label="Status" value={fullAnalysis.status} />
              <Field label="Nivel final" value={formatScoreLevel(finalLevel)} />
              <Field label="ID da analise" value={fullAnalysis.analysis_id ?? analysisDetail?.id ?? "Nao informado"} />
            </CardContent>
          </Card>

          <div className="grid gap-4 md:grid-cols-2">
            <Card className="shadow-sm">
              <CardContent className="space-y-5 pt-5">
                <div>
                  <SectionHeader icon={User} title="Dados principais extraidos" />
                  <div className="grid gap-3 sm:grid-cols-2">
                    <Field label="Profissional" value={fullAnalysis.dados_extraidos?.nome_profissional} />
                    <Field label="Numero ART" value={fullAnalysis.dados_extraidos?.numero_art} />
                    <Field label="Data de inicio" value={fullAnalysis.dados_extraidos?.data_inicio} />
                    <Field label="Data de fim" value={fullAnalysis.dados_extraidos?.data_fim} />
                    <Field label="Data de execucao" value={fullAnalysis.dados_extraidos?.data_execucao} />
                    <Field label="Contratante" value={fullAnalysis.dados_extraidos?.contratante} />
                  </div>
                </div>
                <Separator />
                <div>
                  <SectionHeader icon={Building2} title="Descricao do servico" />
                  <p className="text-sm text-muted-foreground">
                    {fullAnalysis.dados_extraidos?.descricao_servico ?? "Nao foi possivel identificar a descricao do servico."}
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-sm">
              <CardContent className="space-y-5 pt-5">
                <div>
                  <SectionHeader icon={FileSearch} title="Texto extraido" />
                  <p className="text-xs text-muted-foreground">
                    {fullAnalysis.texto_extraido ? `${fullAnalysis.texto_extraido.length} caracteres extraidos do PDF.` : "Nenhum texto extraido foi retornado."}
                  </p>
                </div>
                <div className="max-h-[360px] overflow-auto rounded-lg border bg-muted/30 p-4 text-sm leading-6 text-muted-foreground">
                  {fullAnalysis.texto_extraido ?? "Texto extraido indisponivel para esta analise."}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="validacao" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <IssueList
              title="Aprovados"
              icon={CheckCircle}
              items={approvedItems}
              emptyText="Nenhum item aprovado automaticamente."
              tone="success"
            />
            <IssueList title="Erros" icon={XCircle} items={combinedIssues.erros} emptyText="Nenhum erro identificado." tone="error" />
            <IssueList
              title="Alertas e Inconsistencias"
              icon={AlertTriangle}
              items={dedupe([...combinedIssues.alertas, ...combinedIssues.inconsistencias])}
              emptyText="Nenhum alerta identificado."
              tone="warning"
            />
          </div>

          <Card className="shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-sm">
                <ArrowRightLeft className="h-4 w-4 text-primary" />
                Comparacao CAT x ART
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap items-center gap-3">
                <StatusBadge status={fullAnalysis.comparacao_art?.consistente ? "Aprovado" : "Revisao"} />
                <p className="text-sm text-muted-foreground">
                  {fullAnalysis.comparacao_art?.resumo ?? "Nenhuma comparacao ART foi retornada para esta analise."}
                </p>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <IssueList
                  title="Inconsistencias de comparacao"
                  icon={XCircle}
                  items={fullAnalysis.comparacao_art?.inconsistencias ?? []}
                  emptyText="Nenhuma inconsistencia entre CAT e ART foi encontrada."
                  tone="error"
                />
                <IssueList
                  title="Alertas de comparacao"
                  icon={AlertTriangle}
                  items={fullAnalysis.comparacao_art?.alertas ?? []}
                  emptyText="Nenhum alerta adicional foi retornado."
                  tone="warning"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="fraude" className="space-y-4">
          <Card className="shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-sm">
                <ShieldAlert className="h-4 w-4 text-destructive" />
                Sinais de risco documental
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap items-center gap-3">
                <StatusBadge status={fullAnalysis.fraude?.fraude_detectada ? "Reprovado" : "Aprovado"} />
                <span className="text-sm text-muted-foreground">
                  Nivel de risco: {formatScoreLevel(fullAnalysis.fraude?.nivel_risco)}
                </span>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <IssueList
                  title="Indicadores"
                  icon={AlertTriangle}
                  items={fullAnalysis.fraude?.indicadores ?? []}
                  emptyText="Nenhum indicador de risco foi retornado."
                  tone={fullAnalysis.fraude?.fraude_detectada ? "error" : "success"}
                />
                <IssueList
                  title="Detalhes"
                  icon={ShieldAlert}
                  items={fullAnalysis.fraude?.detalhes ?? []}
                  emptyText="Nenhuma explicacao detalhada foi retornada."
                  tone="warning"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="score" className="space-y-4">
          <Card className="max-w-3xl shadow-sm">
            <CardContent className="space-y-6 pt-6">
              <div className="text-center">
                <p className="mb-1 text-sm text-muted-foreground">Score Final de Confiabilidade</p>
                <p className={`text-5xl font-bold ${scoreColor}`}>{finalScore}</p>
                <p className="mt-1 text-xs text-muted-foreground">de 100 pontos</p>
              </div>
              <Separator />
              <div className="space-y-4">
                <ScoreBar label="Validacao automatica" score={fullAnalysis.validacao?.score ?? finalScore} />
                <ScoreBar label="Confiabilidade final" score={finalScore} />
                <ScoreBar label="Risco invertido" score={mapRiskToConfidence(fullAnalysis.fraude?.nivel_risco)} />
              </div>
              <div className="space-y-2 rounded-lg border bg-muted/30 p-4 text-sm text-muted-foreground">
                <p className="font-medium text-foreground">Resumo</p>
                <p>{fullAnalysis.score_confiabilidade?.resumo ?? fullAnalysis.resultado.mensagem}</p>
              </div>
              {scoreJustifications.length ? (
                <div className="space-y-2">
                  {scoreJustifications.map((item) => (
                    <div key={item} className="rounded-lg border bg-background p-3 text-sm">
                      {item}
                    </div>
                  ))}
                </div>
              ) : null}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="feedback" className="space-y-4">
          <Card className="max-w-3xl shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-sm">
                <Brain className="h-4 w-4 text-primary" />
                Feedback inteligente
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {feedbackItems.length ? (
                feedbackItems.map((item) => (
                  <div key={`${item.tipo}-${item.mensagem}`} className="rounded-xl border border-border bg-muted/30 p-4">
                    <p className="text-sm font-medium">{item.mensagem}</p>
                    <p className="mt-2 text-sm text-muted-foreground">{item.sugestao}</p>
                  </div>
                ))
              ) : (
                <div className="rounded-xl border border-dashed p-4 text-sm text-muted-foreground">
                  Nenhum feedback adicional foi retornado pela API.
                </div>
              )}

              <div className="rounded-xl border border-primary/10 bg-primary/5 p-4">
                <p className="text-sm leading-6">
                  {fullAnalysis.feedback_inteligente?.resumo_geral ?? "Nao ha resumo adicional para esta analise."}
                </p>
              </div>

              <div className="space-y-2">
                <p className="text-sm font-medium">Recomendacoes prioritarias</p>
                {recommendations.length > 0 ? (
                  recommendations.map((item) => (
                    <div key={item} className="rounded-lg border bg-background p-3 text-sm">
                      {item}
                    </div>
                  ))
                ) : (
                  <div className="rounded-lg border border-dashed p-3 text-sm text-muted-foreground">
                    Nenhuma recomendacao adicional foi retornada.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {isDetailLoading && (
        <p className="text-xs text-muted-foreground">
          Atualizando detalhes completos da analise a partir do historico...
        </p>
      )}
    </div>
  );
}

function dedupe(items: string[]): string[] {
  return Array.from(new Set(items));
}

function mapRiskToConfidence(riskLevel: string | undefined): number {
  if (!riskLevel) {
    return 100;
  }

  const normalized = riskLevel
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase();

  if (normalized === "alto") {
    return 20;
  }
  if (normalized === "medio") {
    return 55;
  }
  return 80;
}

function sanitizeFilename(value: string): string {
  return value.replace(/[^a-zA-Z0-9-_]+/g, "-").replace(/^-+|-+$/g, "");
}
