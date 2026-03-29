import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Clock, FileCheck, TrendingUp } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { fetchHistory, type HistoryResponseItem } from "@/lib/api";
import { mockDashboard } from "@/data/mockData";
import { MetricCard } from "@/components/MetricCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Dashboard() {
  const [history, setHistory] = useState<HistoryResponseItem[]>([]);

  useEffect(() => {
    let active = true;

    fetchHistory()
      .then((response) => {
        if (active) {
          setHistory(response);
        }
      })
      .catch(() => {
        if (active) {
          setHistory([]);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  const metrics = useMemo(() => {
    if (history.length === 0) {
      return {
        totalAnalisadas: mockDashboard.totalAnalisadas,
        tempoMedio: mockDashboard.tempoMedio,
        taxaErro: mockDashboard.taxaErro,
        taxaAprovacao: 78,
      };
    }

    const total = history.length;
    const reprovadas = history.filter((item) => item.score < 50).length;
    const aprovadas = history.filter((item) => item.score >= 80).length;

    return {
      totalAnalisadas: total,
      tempoMedio: "1.8s",
      taxaErro: Number(((reprovadas / total) * 100).toFixed(1)),
      taxaAprovacao: Number(((aprovadas / total) * 100).toFixed(0)),
    };
  }, [history]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Dashboard</h2>
        <p className="mt-1 text-sm text-muted-foreground">Visao geral das analises de CAT</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard title="CATs Analisadas" value={metrics.totalAnalisadas} subtitle="Total acumulado" icon={FileCheck} />
        <MetricCard title="Tempo Medio" value={metrics.tempoMedio} subtitle="Por analise" icon={Clock} />
        <MetricCard title="Taxa de Erro" value={`${metrics.taxaErro}%`} subtitle="Ultimas analises" icon={AlertTriangle} />
        <MetricCard title="Taxa de Aprovacao" value={`${metrics.taxaAprovacao}%`} subtitle="Ultimas analises" icon={TrendingUp} />
      </div>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-base">Analises por Mes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockDashboard.chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(214 20% 90%)" />
                <XAxis dataKey="mes" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="aprovadas" name="Aprovadas" fill="hsl(142 71% 45%)" radius={[3, 3, 0, 0]} />
                <Bar dataKey="revisao" name="Revisao" fill="hsl(38 92% 50%)" radius={[3, 3, 0, 0]} />
                <Bar dataKey="reprovadas" name="Reprovadas" fill="hsl(0 72% 51%)" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
