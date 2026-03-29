import { useEffect, useMemo, useState } from "react";
import { FileText } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { fetchHistory, type AnalyzeResponse, type HistoryResponseItem } from "@/lib/api";
import { formatBackendDate, getStatusFromScore, type UiAnalysisStatus } from "@/lib/analysis-utils";
import { mockHistory } from "@/data/mockData";
import { StatusBadge } from "@/components/StatusBadge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";


type UiHistoryItem = {
  id: string;
  nome: string;
  data: string;
  score: number;
  status: UiAnalysisStatus;
};

export default function Historico() {
  const navigate = useNavigate();
  const [items, setItems] = useState<UiHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [usingFallback, setUsingFallback] = useState(false);

  useEffect(() => {
    let active = true;

    fetchHistory()
      .then((response) => {
        if (!active) {
          return;
        }

        setItems(mapHistoryToUi(response));
        setUsingFallback(false);
      })
      .catch(() => {
        if (!active) {
          return;
        }

        setItems(
          mockHistory.map((item) => ({
            id: item.id,
            nome: item.nome,
            data: item.data,
            score: item.score,
            status: normalizeStatus(item.status),
          })),
        );
        setUsingFallback(true);
      })
      .finally(() => {
        if (active) {
          setIsLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  const emptyMessage = useMemo(() => {
    if (isLoading) {
      return "Carregando historico...";
    }
    if (usingFallback) {
      return "Historico exibido com dados de demonstracao.";
    }
    return "Nenhuma analise registrada ate o momento.";
  }, [isLoading, usingFallback]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Historico</h2>
        <p className="mt-1 text-sm text-muted-foreground">Todas as CATs analisadas</p>
      </div>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-base">CATs Analisadas</CardTitle>
        </CardHeader>
        <CardContent>
          {items.length === 0 ? (
            <div className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">
              {emptyMessage}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Documento</TableHead>
                  <TableHead>Data</TableHead>
                  <TableHead className="text-center">Score</TableHead>
                  <TableHead className="text-center">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((item) => (
                  <TableRow
                    key={item.id}
                    className="cursor-pointer transition-colors hover:bg-accent/40"
                    onClick={() => handleOpenAnalysis(item, navigate)}
                  >
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm font-medium">{item.nome}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">{item.data}</TableCell>
                    <TableCell className="text-center">
                      <span
                        className={`text-sm font-semibold ${
                          item.score >= 80 ? "text-success" : item.score >= 50 ? "text-warning" : "text-destructive"
                        }`}
                      >
                        {item.score}
                      </span>
                    </TableCell>
                    <TableCell className="text-center">
                      <StatusBadge status={item.status} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function mapHistoryToUi(items: HistoryResponseItem[]): UiHistoryItem[] {
  return items.map((item) => ({
    id: item.id.toString(),
    nome: item.filename,
    data: formatBackendDate(item.data_criacao),
    score: item.score,
    status: getStatusFromScore(item.score),
  }));
}

function normalizeStatus(value: string): UiAnalysisStatus {
  if (value === "Aprovado") {
    return "Aprovado";
  }
  if (value === "Revisao" || value === "RevisÃ£o") {
    return "Revisao";
  }
  return "Reprovado";
}

function handleOpenAnalysis(item: UiHistoryItem, navigate: ReturnType<typeof useNavigate>) {
  const analysis: AnalyzeResponse = {
    analysis_id: Number(item.id),
    filename: item.nome,
    status: "processado",
    resultado: {
      mensagem: "Analise carregada do historico.",
      score: item.score,
      nivel: item.status === "Aprovado" ? "alto" : item.status === "Revisao" ? "medio" : "baixo",
    },
  };

  navigate("/analise", { state: { analysis } });
}
