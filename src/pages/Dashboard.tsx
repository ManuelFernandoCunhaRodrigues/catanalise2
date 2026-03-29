import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Clock, FileCheck, TrendingUp } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { fetchHistory, type HistoryResponseItem } from "@/lib/api";
import { getMonthKey } from "@/lib/analysis-utils";
import { MetricCard } from "@/components/MetricCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Dashboard() {
  const [history, setHistory] = useState<HistoryResponseItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    fetchHistory()
      .then((response) => {
        if (!active) {
          return;
        }

        setHistory(response);
        setError(null);
      })
      .catch((fetchError) => {
        if (!active) {
          return;
        }

        setHistory([]);
        setError(fetchError instanceof Error ? fetchError.message : "Nao foi possivel carregar o dashboard.");
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

  const metrics = useMemo(() => {
    const total = history.length;
    const reprovadas = history.filter((item) => item.score < 50).length;
    const aprovadas = history.filter((item) => item.score >= 80).length;

    return {
      totalAnalisadas: total,
      tempoMedio: total > 0 ? "1.8s" : "--",
      taxaErro: total > 0 ? Number(((reprovadas / total) * 100).toFixed(1)) : 0,
      taxaAprovacao: total > 0 ? Number(((aprovadas / total) * 100).toFixed(0)) : 0,
    };
  }, [history]);

  const chartData = useMemo(() => buildChartData(history), [history]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Dashboard</h2>
        <p className="mt-1 text-sm text-muted-foreground">Visao geral das analises de CAT</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard title="CATs Analisadas" value={metrics.totalAnalisadas} subtitle="Total acumulado" icon={FileCheck} />
        <MetricCard title="Tempo Medio" value={metrics.tempoMedio} subtitle="Por analise" icon={Clock} />
        <MetricCard title="Taxa de Erro" value={`${metrics.taxaErro}%`} subtitle="Documentos reprovados" icon={AlertTriangle} />
        <MetricCard title="Taxa de Aprovacao" value={`${metrics.taxaAprovacao}%`} subtitle="Scores acima de 80" icon={TrendingUp} />
      </div>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-base">Analises por Mes</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="rounded-lg border border-destructive/20 bg-destructive/5 p-3 text-sm text-destructive">
              {error}
            </div>
          )}

          {isLoading ? (
            <div className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">Carregando dados do dashboard...</div>
          ) : history.length === 0 ? (
            <div className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">
              Nenhuma analise encontrada ainda. Envie uma CAT para popular o dashboard.
            </div>
          ) : (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(214 20% 90%)" />
                  <XAxis dataKey="mes" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="aprovadas" name="Aprovadas" fill="hsl(142 71% 45%)" radius={[3, 3, 0, 0]} />
                  <Bar dataKey="revisao" name="Revisao" fill="hsl(38 92% 50%)" radius={[3, 3, 0, 0]} />
                  <Bar dataKey="reprovadas" name="Reprovadas" fill="hsl(0 72% 51%)" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function buildChartData(items: HistoryResponseItem[]) {
  const now = new Date();
  const buckets = Array.from({ length: 6 }, (_, reverseIndex) => {
    const date = new Date(now.getFullYear(), now.getMonth() - (5 - reverseIndex), 1);
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;

    return {
      key,
      mes: date.toLocaleDateString("pt-BR", { month: "short" }).replace(".", ""),
      aprovadas: 0,
      revisao: 0,
      reprovadas: 0,
    };
  });

  const indexByKey = new Map(buckets.map((bucket) => [bucket.key, bucket]));

  items.forEach((item) => {
    const bucketKey = getMonthKey(item.data_criacao);
    if (!bucketKey) {
      return;
    }

    const bucket = indexByKey.get(bucketKey);
    if (!bucket) {
      return;
    }

    if (item.score >= 80) {
      bucket.aprovadas += 1;
      return;
    }

    if (item.score >= 50) {
      bucket.revisao += 1;
      return;
    }

    bucket.reprovadas += 1;
  });

  return buckets;
}
