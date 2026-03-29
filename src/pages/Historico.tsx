import { useEffect, useMemo, useState } from "react";
import { FileText } from "lucide-react";
import { useNavigate, type NavigateFunction } from "react-router-dom";

import { fetchHistory, type AnalyzeResponse, type HistoryResponseItem } from "@/lib/api";
import { formatBackendDate, formatScoreLevel, getStatusFromScore, type UiAnalysisStatus } from "@/lib/analysis-utils";
import { StatusBadge } from "@/components/StatusBadge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

type UiHistoryItem = {
  id: number;
  nome: string;
  data: string;
  score: number;
  nivel: string;
  status: UiAnalysisStatus;
};

export default function Historico() {
  const navigate = useNavigate();
  const [items, setItems] = useState<UiHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    fetchHistory()
      .then((response) => {
        if (!active) {
          return;
        }

        setItems(mapHistoryToUi(response));
        setError(null);
      })
      .catch((fetchError) => {
        if (!active) {
          return;
        }

        setItems([]);
        setError(fetchError instanceof Error ? fetchError.message : "Nao foi possivel carregar o historico.");
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
    if (error) {
      return error;
    }
    return "Nenhuma analise registrada ate o momento.";
  }, [error, isLoading]);

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
                  <TableHead>Nivel</TableHead>
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
                    <TableCell className="text-sm text-muted-foreground">{item.nivel}</TableCell>
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
    id: item.id,
    nome: item.filename,
    data: formatBackendDate(item.data_criacao),
    score: item.score,
    nivel: formatScoreLevel(item.nivel),
    status: getStatusFromScore(item.score),
  }));
}

function handleOpenAnalysis(item: UiHistoryItem, navigate: NavigateFunction) {
  const analysis: AnalyzeResponse = {
    analysis_id: item.id,
    filename: item.nome,
    status: "processado",
    resultado: {
      mensagem: "Analise carregada do historico.",
      score: item.score,
      nivel: item.nivel.toLowerCase(),
    },
  };

  navigate("/analise", { state: { analysis } });
}
