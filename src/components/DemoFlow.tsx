import { useEffect, useMemo, useRef, useState, type ElementType } from "react";
import {
  AlertTriangle,
  Brain,
  CheckCircle2,
  Clock3,
  FileJson,
  FileSearch,
  History,
  PlayCircle,
  ShieldAlert,
  Sparkles,
  Upload,
} from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

import { demoScenario } from "@/data/mockData";
import { StatusBadge } from "@/components/StatusBadge";
import { ScoreBar } from "@/components/ScoreBar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";


type DemoStatus = "idle" | "uploaded" | "analyzing" | "processed";
type StepKey =
  | "upload"
  | "processing"
  | "extraction"
  | "validation"
  | "fraud"
  | "score"
  | "feedback"
  | "saved"
  | "history";

interface DemoStep {
  key: StepKey;
  title: string;
  description: string;
  bancaMessage: string;
  status: DemoStatus;
}

const steps: DemoStep[] = [
  {
    key: "upload",
    title: "Passo 1: Upload do arquivo exemplo",
    description: "A demonstracao comeca com um documento pronto para revelar problemas reais de negocio.",
    bancaMessage: "Comecamos com um upload guiado para evitar friccao e garantir uma demonstracao previsivel.",
    status: "uploaded",
  },
  {
    key: "processing",
    title: "Passo 2: Processando documento",
    description: "O sistema comunica visualmente que a analise esta em andamento.",
    bancaMessage: "Estados claros reduzem ansiedade do usuario e melhoram a percepcao de confiabilidade da plataforma.",
    status: "analyzing",
  },
  {
    key: "extraction",
    title: "Passo 3: Exibicao dos dados extraidos",
    description: "O PDF vira estrutura pronta para revisao e integracao com regras de negocio.",
    bancaMessage: "Aqui mostramos a transformacao de documento em dado estruturado, que e a base de todo o motor.",
    status: "analyzing",
  },
  {
    key: "validation",
    title: "Passo 4: Validacao automatica",
    description: "Erros, alertas e inconsistencias sao separados para facilitar a decisao.",
    bancaMessage: "A triagem automatica reduz retrabalho e padroniza a leitura de documentos tecnicos.",
    status: "analyzing",
  },
  {
    key: "fraud",
    title: "Passo 5: Deteccao de fraude",
    description: "O sistema identifica sinais de risco documental de forma explicavel.",
    bancaMessage: "Nao mostramos apenas falhas de preenchimento, mas tambem risco documental e incoerencia tecnica.",
    status: "analyzing",
  },
  {
    key: "score",
    title: "Passo 6: Score de confiabilidade",
    description: "Regras e riscos sao convertidos em um indicador unico para priorizacao.",
    bancaMessage: "O score ajuda a banca a entender como o produto apoia decisao e prioriza analise humana.",
    status: "analyzing",
  },
  {
    key: "feedback",
    title: "Passo 7: Feedback inteligente",
    description: "O usuario recebe orientacao pratica sobre o que corrigir antes da submissao.",
    bancaMessage: "O produto nao apenas aponta o problema, ele ensina como corrigir e reduz retrabalho operacional.",
    status: "analyzing",
  },
  {
    key: "saved",
    title: "Passo 8: Persistencia no historico",
    description: "A analise e salva para rastreabilidade e auditoria posterior.",
    bancaMessage: "Persistencia transforma a demonstracao em fluxo real de produto, nao em prototipo superficial.",
    status: "processed",
  },
  {
    key: "history",
    title: "Passo 9: Historico atualizado",
    description: "Fechamos a jornada mostrando o documento ja salvo para consulta.",
    bancaMessage: "Em menos de dois minutos mostramos o ciclo completo: problema, solucao, decisao e rastreabilidade.",
    status: "processed",
  },
];

const stepDelayMs = 1300;

function sleep(ms: number) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

function JsonPanel({ title, data }: { title: string; data: unknown }) {
  return (
    <Card className="shadow-sm">
      <CardHeader className="pb-3">
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <pre className="overflow-x-auto rounded-lg bg-slate-950 p-4 text-xs leading-6 text-slate-100">
          {JSON.stringify(data, null, 2)}
        </pre>
      </CardContent>
    </Card>
  );
}

function InfoList({
  title,
  icon: Icon,
  items,
  tone,
}: {
  title: string;
  icon: ElementType;
  items: string[];
  tone: "error" | "warning" | "info";
}) {
  const toneClasses = {
    error: "border-destructive/20 bg-destructive/5 text-destructive",
    warning: "border-warning/20 bg-warning/5 text-warning",
    info: "border-primary/15 bg-primary/5 text-primary",
  };

  return (
    <Card className="shadow-sm">
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Icon className="h-4 w-4" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {items.map((item) => (
          <div key={item} className={cn("rounded-lg border p-3 text-sm", toneClasses[tone])}>
            {item}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

export function DemoFlow() {
  const [activeStepIndex, setActiveStepIndex] = useState(-1);
  const [completedKeys, setCompletedKeys] = useState<StepKey[]>([]);
  const [demoStatus, setDemoStatus] = useState<DemoStatus>("idle");
  const [isRunning, setIsRunning] = useState(false);
  const runIdRef = useRef(0);

  useEffect(() => {
    return () => {
      runIdRef.current += 1;
    };
  }, []);

  const progressValue = useMemo(() => {
    if (completedKeys.length === 0) {
      return 0;
    }
    return Math.round((completedKeys.length / steps.length) * 100);
  }, [completedKeys.length]);

  const activeStep = activeStepIndex >= 0 ? steps[activeStepIndex] : null;

  const startDemo = async () => {
    runIdRef.current += 1;
    const currentRun = runIdRef.current;

    setIsRunning(true);
    setActiveStepIndex(-1);
    setCompletedKeys([]);
    setDemoStatus("idle");

    for (let index = 0; index < steps.length; index += 1) {
      const step = steps[index];
      if (currentRun !== runIdRef.current) {
        return;
      }

      setActiveStepIndex(index);
      setDemoStatus(step.status);
      setCompletedKeys((previous) => [...previous.filter((item) => item !== step.key), step.key]);
      await sleep(stepDelayMs);
    }

    if (currentRun === runIdRef.current) {
      setIsRunning(false);
    }
  };

  const visible = (key: StepKey) => completedKeys.includes(key);

  const statusCards = [
    {
      label: "Upload realizado",
      active: demoStatus === "uploaded" || demoStatus === "analyzing" || demoStatus === "processed",
      icon: Upload,
    },
    {
      label: "Analisando...",
      active: demoStatus === "analyzing",
      icon: Clock3,
    },
    {
      label: "Processado",
      active: demoStatus === "processed",
      icon: CheckCircle2,
    },
  ];

  return (
    <div className="space-y-6">
      <Card className="overflow-hidden border-primary/15 bg-gradient-to-br from-primary/10 via-background to-warning/10 shadow-sm">
        <CardContent className="p-0">
          <div className="grid gap-6 p-6 lg:grid-cols-[1.2fr_0.8fr]">
            <div className="space-y-4">
              <Badge variant="outline" className="border-primary/20 bg-primary/5 text-primary">
                Modo Demo
              </Badge>
              <div className="space-y-2">
                <h3 className="text-3xl font-semibold tracking-tight">Apresentacao guiada do produto em menos de 2 minutos</h3>
                <p className="max-w-2xl text-sm leading-6 text-muted-foreground">
                  O fluxo simula uma analise completa de CAT, mostrando upload, extracao, validacao, risco, score,
                  feedback inteligente e historico com mensagens pensadas para a banca.
                </p>
              </div>
              <div className="flex flex-wrap gap-3">
                <Button size="lg" onClick={startDemo} disabled={isRunning}>
                  <PlayCircle className="h-4 w-4" />
                  {isRunning ? "Demonstracao em andamento" : "Iniciar Demonstracao"}
                </Button>
                <Button variant="outline" size="lg" onClick={startDemo}>
                  Reiniciar roteiro
                </Button>
              </div>
            </div>

            <Card className="border-white/60 bg-white/70 shadow-none backdrop-blur">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Narrativa para a banca</CardTitle>
                <CardDescription>Explicacao curta e clara do valor do sistema a cada etapa.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-xl border border-primary/10 bg-primary/5 p-4">
                  <p className="text-sm leading-6 text-foreground">
                    {activeStep?.bancaMessage ??
                      "Clique em Iniciar Demonstracao para conduzir a banca por todo o fluxo do produto."}
                  </p>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs uppercase tracking-[0.2em] text-muted-foreground">
                    <span>Progresso</span>
                    <span>{progressValue}%</span>
                  </div>
                  <Progress value={progressValue} className="h-3" />
                </div>
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-[0.95fr_1.05fr]">
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="text-base">Etapas da demonstracao</CardTitle>
            <CardDescription>Uma sequencia guiada para mostrar o produto sem depender de explicacao verbal complexa.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {steps.map((step, index) => {
              const isActive = activeStepIndex === index;
              const isCompleted = completedKeys.includes(step.key);

              return (
                <div
                  key={step.key}
                  className={cn(
                    "rounded-xl border p-4 transition-all",
                    isActive && "border-primary bg-primary/5 shadow-sm",
                    !isActive && isCompleted && "border-success/20 bg-success/5",
                    !isActive && !isCompleted && "border-border bg-card",
                  )}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="space-y-1">
                      <p className="text-sm font-medium">{step.title}</p>
                      <p className="text-xs leading-5 text-muted-foreground">{step.description}</p>
                    </div>
                    <Badge
                      variant="outline"
                      className={cn(
                        isActive && "border-primary/20 bg-primary/10 text-primary",
                        !isActive && isCompleted && "border-success/20 bg-success/10 text-success",
                      )}
                    >
                      {isActive ? "Ao vivo" : isCompleted ? "Concluido" : "Aguardando"}
                    </Badge>
                  </div>
                </div>
              );
            })}
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card className="shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Status visual</CardTitle>
              <CardDescription>Estados simples para a banca entender o fluxo em tempo real.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-3 sm:grid-cols-3">
              {statusCards.map(({ label, active, icon: Icon }) => (
                <div
                  key={label}
                  className={cn(
                    "rounded-xl border p-4 transition-all",
                    active ? "border-primary/20 bg-primary/10" : "border-border bg-muted/30",
                  )}
                >
                  <div className="flex items-center gap-3">
                    <div className={cn("rounded-lg p-2", active ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground")}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="text-sm font-medium">{label}</p>
                      <p className="text-xs text-muted-foreground">{active ? "Estado ativo" : "Aguardando"}</p>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <AnimatePresence mode="popLayout">
            {visible("upload") && (
              <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}>
                <Card className="shadow-sm">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <Upload className="h-4 w-4 text-primary" />
                      Arquivo carregado
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="rounded-xl border border-primary/10 bg-primary/5 p-4">
                      <p className="text-sm font-medium">{demoScenario.fileName}</p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        Documento exemplo preparado para mostrar erros reais de negocio durante a apresentacao.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {visible("processing") && (
              <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}>
                <Card className="shadow-sm">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-primary" />
                      Processando documento...
                    </CardTitle>
                    <CardDescription>Extraindo estrutura, aplicando regras e preparando evidencias para decisao.</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Progress value={Math.max(progressValue, 20)} className="h-3" />
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {visible("extraction") && (
              <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}>
                <JsonPanel title="Dados extraidos da CAT" data={demoScenario.extractedData} />
              </motion.div>
            )}

            {visible("validation") && (
              <motion.div
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -12 }}
                className="grid gap-4 md:grid-cols-3"
              >
                <InfoList title="Erros" icon={AlertTriangle} items={demoScenario.validations.erros} tone="error" />
                <InfoList title="Alertas" icon={FileSearch} items={demoScenario.validations.alertas} tone="warning" />
                <InfoList title="Inconsistencias" icon={FileJson} items={demoScenario.validations.inconsistencias} tone="info" />
              </motion.div>
            )}

            {visible("fraud") && (
              <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}>
                <Card className="shadow-sm">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <ShieldAlert className="h-4 w-4 text-destructive" />
                      Deteccao de fraude
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex flex-wrap items-center gap-3">
                      <Badge variant="outline" className="border-destructive/20 bg-destructive/10 text-destructive">
                        Fraude detectada
                      </Badge>
                      <Badge variant="outline" className="border-warning/20 bg-warning/10 text-warning">
                        Risco {demoScenario.fraud.nivel_risco}
                      </Badge>
                    </div>
                    <div className="grid gap-3 md:grid-cols-2">
                      <div className="space-y-2">
                        <p className="text-sm font-medium">Indicadores</p>
                        {demoScenario.fraud.indicadores.map((item) => (
                          <div key={item} className="rounded-lg border border-destructive/20 bg-destructive/5 p-3 text-sm text-destructive">
                            {item}
                          </div>
                        ))}
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm font-medium">Explicacao para a banca</p>
                        {demoScenario.fraud.detalhes.map((item) => (
                          <div key={item} className="rounded-lg border border-border bg-muted/40 p-3 text-sm">
                            {item}
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {visible("score") && (
              <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}>
                <Card className="shadow-sm">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base">Score de confiabilidade</CardTitle>
                  </CardHeader>
                  <CardContent className="grid gap-6 md:grid-cols-[0.35fr_0.65fr]">
                    <div className="rounded-2xl border border-destructive/20 bg-destructive/5 p-6 text-center">
                      <p className="text-sm text-muted-foreground">Score final</p>
                      <p className="mt-2 text-5xl font-bold text-destructive">{demoScenario.reliabilityScore.score}</p>
                      <p className="mt-2 text-sm font-medium capitalize">{demoScenario.reliabilityScore.nivel}</p>
                    </div>
                    <div className="space-y-4">
                      <ScoreBar label="Confiabilidade documental" score={demoScenario.reliabilityScore.score} />
                      <div className="space-y-2">
                        {demoScenario.reliabilityScore.justificativa.map((item) => (
                          <div key={item} className="rounded-lg border border-border bg-muted/40 p-3 text-sm">
                            {item}
                          </div>
                        ))}
                      </div>
                      <p className="text-sm leading-6 text-muted-foreground">{demoScenario.reliabilityScore.resumo}</p>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {visible("feedback") && (
              <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}>
                <Card className="shadow-sm">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <Brain className="h-4 w-4 text-primary" />
                      Feedback inteligente
                    </CardTitle>
                    <CardDescription>O sistema explica o problema e diz exatamente como corrigir.</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {demoScenario.intelligentFeedback.feedback.map((item) => (
                      <div key={`${item.tipo}-${item.mensagem}`} className="rounded-xl border border-border bg-muted/40 p-4">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="capitalize">
                            {item.tipo}
                          </Badge>
                          <p className="text-sm font-medium">{item.mensagem}</p>
                        </div>
                        <p className="mt-2 text-sm text-muted-foreground">{item.sugestao}</p>
                      </div>
                    ))}
                    <div className="rounded-xl border border-primary/10 bg-primary/5 p-4">
                      <p className="text-sm leading-6">{demoScenario.intelligentFeedback.resumo_geral}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium">Recomendacoes prioritarias</p>
                      {demoScenario.intelligentFeedback.recomendacoes.map((item) => (
                        <div key={item} className="rounded-lg border border-border bg-background p-3 text-sm">
                          {item}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {visible("saved") && (
              <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}>
                <Card className="shadow-sm">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-success" />
                      Analise salva com sucesso
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="flex items-center justify-between gap-4 rounded-xl border border-success/20 bg-success/5 p-4">
                    <div>
                      <p className="text-sm font-medium">{demoScenario.historyItem.nome}</p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        O registro foi persistido no historico para rastreabilidade e consulta posterior.
                      </p>
                    </div>
                    <StatusBadge status={demoScenario.historyItem.status} />
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {visible("history") && (
              <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}>
                <Card className="shadow-sm">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <History className="h-4 w-4 text-primary" />
                      Historico atualizado
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-3 rounded-xl border p-4 md:grid-cols-[1fr_auto_auto] md:items-center">
                      <div>
                        <p className="text-sm font-medium">{demoScenario.historyItem.nome}</p>
                        <p className="text-xs text-muted-foreground">{demoScenario.historyItem.data}</p>
                      </div>
                      <p className="text-lg font-semibold text-destructive">{demoScenario.historyItem.score}</p>
                      <StatusBadge status={demoScenario.historyItem.status} />
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
