import { useEffect, useMemo, useState, type ElementType } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  Brain,
  Building2,
  CheckCircle,
  Download,
  Edit,
  FileText,
  HardHat,
  MapPin,
  PenTool,
  RefreshCw,
  User,
  XCircle,
} from "lucide-react";

import { fetchHistoryById, type AnalyzeResponse, type HistoryDetailResponse } from "@/lib/api";
import { getLastAnalysis, saveLastAnalysis } from "@/lib/analysis-store";
import { getStatusFromScore } from "@/lib/analysis-utils";
import { mockExtractedData, mockFeedback, mockScore } from "@/data/mockData";
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

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-sm">{value}</p>
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
        <CardTitle className="text-sm flex items-center gap-2">
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
      setIsDetailLoading(false);
      return;
    }

    let active = true;
    setDetailError(null);
    setIsDetailLoading(true);

    fetchHistoryById(analysis.analysis_id)
      .then((detail) => {
        if (active) {
          setAnalysisDetail(detail);
        }
      })
      .catch((error) => {
        if (active) {
          setAnalysisDetail(null);
          setDetailError(error instanceof Error ? error.message : "Nao foi possivel carregar os detalhes da analise.");
        }
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

  const documentData = mockExtractedData;
  const documentName = analysis?.filename ?? "CAT-2024-0847.pdf";
  const apiScore = analysis?.resultado.score ?? mockScore.geral;
  const apiLevel = analysis?.resultado.nivel ?? "medio";
  const apiMessage = analysis?.resultado.mensagem ?? "Resultado carregado do cenario demonstrativo.";
  const status = useMemo(() => getStatusFromScore(apiScore), [apiScore]);
  const scoreColor = apiScore >= 80 ? "text-success" : apiScore >= 50 ? "text-warning" : "text-destructive";

  const validationData = useMemo(() => {
    if (analysisDetail) {
      return {
        aprovados:
          analysisDetail.erros.length === 0 && analysisDetail.alertas.length === 0 && analysisDetail.inconsistencias.length === 0
            ? ["Nenhum problema critico identificado nesta analise."]
            : ["Documento processado e disponivel para auditoria no historico."],
        erros: analysisDetail.erros,
        alertas: analysisDetail.alertas,
        inconsistencias: analysisDetail.inconsistencias,
      };
    }

    if (isDetailLoading) {
      return {
        aprovados: ["Carregando detalhes da analise..."],
        erros: ["Carregando erros da analise..."],
        alertas: ["Carregando alertas da analise..."],
        inconsistencias: ["Carregando inconsistencias da analise..."],
      };
    }

    return {
      aprovados: ["Documento processado e disponivel para auditoria no historico."],
      erros: ["Nenhum erro retornado pela API para esta analise."],
      alertas: ["Nenhum alerta retornado pela API para esta analise."],
      inconsistencias: ["Nenhuma inconsistencia retornada pela API para esta analise."],
    };
  }, [analysisDetail, isDetailLoading]);

  const feedbackText = useMemo(() => {
    if (!analysisDetail) {
      return mockFeedback;
    }

    const parts = [
      ...analysisDetail.erros.map((item) => `Erro identificado: ${item}.`),
      ...analysisDetail.alertas.map((item) => `Alerta importante: ${item}.`),
      ...analysisDetail.inconsistencias.map((item) => `Inconsistencia encontrada: ${item}.`),
    ];

    return parts.length > 0
      ? `${parts.join(" ")} Recomenda-se revisar o documento antes da aprovacao final.`
      : "A analise historica nao retornou problemas criticos. O documento esta pronto para seguir no fluxo.";
  }, [analysisDetail]);

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
          <Button size="sm" disabled>
            <Download className="mr-1.5 h-3.5 w-3.5" />
            Relatorio
          </Button>
        </div>
      </div>

      <Card className="shadow-sm">
        <CardContent className="flex flex-col gap-4 pt-6 md:flex-row md:items-center md:justify-between">
          <div className="space-y-2">
            <p className="text-sm font-medium">Resumo da API</p>
            <p className="text-sm text-muted-foreground">{apiMessage}</p>
            {analysis?.analysis_id && <p className="text-xs text-muted-foreground">ID da analise: {analysis.analysis_id}</p>}
            {detailError && <p className="text-xs text-destructive">{detailError}</p>}
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <StatusBadge status={status} />
            <span className={`text-2xl font-bold ${scoreColor}`}>{apiScore}</span>
            <span className="text-sm capitalize text-muted-foreground">{apiLevel}</span>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="extracao" className="space-y-4">
        <TabsList className="grid w-full max-w-lg grid-cols-4">
          <TabsTrigger value="extracao">Extracao</TabsTrigger>
          <TabsTrigger value="validacao">Validacao</TabsTrigger>
          <TabsTrigger value="score">Score</TabsTrigger>
          <TabsTrigger value="feedback">Feedback IA</TabsTrigger>
        </TabsList>

        <TabsContent value="extracao" className="space-y-4">
          <Card className="shadow-sm">
            <CardContent className="grid gap-4 pt-6 md:grid-cols-3">
              <Field label="Documento" value={documentName} />
              <Field label="Status" value={analysis?.status ?? "processado"} />
              <Field label="Nivel retornado" value={apiLevel} />
            </CardContent>
          </Card>

          <div className="grid gap-4 md:grid-cols-2">
            <Card className="shadow-sm">
              <CardContent className="space-y-5 pt-5">
                <div>
                  <SectionHeader icon={MapPin} title="Dados da Obra/Servico" />
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="Contrato" value={documentData.obra.contrato} />
                    <Field label="Prazo" value={documentData.obra.prazoContratual} />
                    <Field label="Inicio" value={documentData.obra.periodoInicio} />
                    <Field label="Fim" value={documentData.obra.periodoFim} />
                    <div className="col-span-2">
                      <Field label="Endereco" value={documentData.obra.endereco} />
                    </div>
                    <Field label="Parcelas Executadas" value={documentData.obra.parcelasExecutadas} />
                  </div>
                </div>
                <Separator />
                <div>
                  <SectionHeader icon={User} title="Contratante" />
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="Tipo" value={documentData.contratante.tipo} />
                    <Field label="Documento" value={documentData.contratante.documento} />
                    <div className="col-span-2">
                      <Field label="Nome/Razao Social" value={documentData.contratante.nome} />
                    </div>
                  </div>
                </div>
                <Separator />
                <div>
                  <SectionHeader icon={Building2} title="Contratada" />
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="Razao Social" value={documentData.contratada.razaoSocial} />
                    <Field label="CNPJ" value={documentData.contratada.cnpj} />
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="space-y-4">
              <Card className="shadow-sm">
                <CardContent className="pt-5">
                  <SectionHeader icon={HardHat} title="Responsaveis Tecnicos" />
                  <div className="space-y-3">
                    {documentData.responsaveis.map((responsavel) => (
                      <div key={`${responsavel.nome}-${responsavel.rnp}`} className="space-y-1.5 rounded-lg bg-secondary/50 p-3">
                        <p className="text-sm font-medium">{responsavel.nome}</p>
                        <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                          <span>Titulo: {responsavel.titulo}</span>
                          <span>RNP: {responsavel.rnp}</span>
                          <span className="col-span-2">CREA: {responsavel.crea}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-sm">
                <CardContent className="pt-5">
                  <SectionHeader icon={FileText} title="Descricao dos Servicos" />
                  <p className="mb-3 text-sm text-muted-foreground">{documentData.servicos.descricao}</p>
                  <div className="overflow-hidden rounded-lg border">
                    <table className="w-full text-sm">
                      <thead className="bg-secondary/50">
                        <tr>
                          <th className="p-2 text-left font-medium">Item</th>
                          <th className="p-2 text-left font-medium">Un.</th>
                          <th className="p-2 text-right font-medium">Qtd.</th>
                        </tr>
                      </thead>
                      <tbody>
                        {documentData.servicos.quantitativos.map((quantitativo) => (
                          <tr key={`${quantitativo.item}-${quantitativo.unidade}`} className="border-t">
                            <td className="p-2">{quantitativo.item}</td>
                            <td className="p-2">{quantitativo.unidade}</td>
                            <td className="p-2 text-right">{quantitativo.quantidade}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-sm">
                <CardContent className="pt-5">
                  <SectionHeader icon={PenTool} title="Assinaturas" />
                  <div className="space-y-2">
                    <Field label="Representante do Contratante" value={documentData.assinaturas.representanteContratante} />
                    <Field label="Profissional Habilitado" value={documentData.assinaturas.profissionalHabilitado} />
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="validacao" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <IssueList
              title="Aprovados"
              icon={CheckCircle}
              items={validationData.aprovados}
              emptyText="Nenhum item aprovado automaticamente."
              tone="success"
            />
            <IssueList title="Erros" icon={XCircle} items={validationData.erros} emptyText="Nenhum erro identificado." tone="error" />
            <IssueList
              title="Alertas e Inconsistencias"
              icon={AlertTriangle}
              items={[...validationData.alertas, ...validationData.inconsistencias]}
              emptyText="Nenhum alerta identificado."
              tone="warning"
            />
          </div>
        </TabsContent>

        <TabsContent value="score" className="space-y-4">
          <Card className="max-w-lg shadow-sm">
            <CardContent className="space-y-6 pt-6">
              <div className="text-center">
                <p className="mb-1 text-sm text-muted-foreground">Score Geral</p>
                <p className={`text-5xl font-bold ${scoreColor}`}>{apiScore}</p>
                <p className="mt-1 text-xs text-muted-foreground">de 100 pontos</p>
              </div>
              <Separator />
              <div className="space-y-4">
                <ScoreBar label="Completude" score={Math.max(35, apiScore)} />
                <ScoreBar label="Consistencia" score={Math.max(25, apiScore - 8)} />
                <ScoreBar label="Confiabilidade" score={apiScore} />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="feedback" className="space-y-4">
          <Card className="max-w-2xl shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center gap-2">
                <Brain className="h-4 w-4 text-primary" />
                Feedback Inteligente
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="rounded-lg border border-primary/10 bg-accent/50 p-4">
                <p className="text-sm leading-relaxed">{feedbackText || mockFeedback}</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
