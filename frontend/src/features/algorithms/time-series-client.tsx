"use client";

import { useMutation } from "@tanstack/react-query";
import { CalendarClock, LineChart as LineChartIcon, Sigma, Target } from "lucide-react";
import { useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { toast } from "sonner";
import { AlgorithmGuard } from "@/features/algorithms/algorithm-guard";
import { DiagramGallery } from "@/components/analytics/diagram-gallery";
import { MetricCard } from "@/components/analytics/metric-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/services/api";
import { useAnalyticsStore } from "@/store/session-store";
import type { DiagramsResponseDTO, TimeSeriesMethodType, TimeSeriesRunResponseDTO } from "@/types/api";
import { forecastData } from "@/utils/demo-data";
import { safeJsonStringify, titleCase } from "@/lib/utils";

const methods: TimeSeriesMethodType[] = ["linear_regression", "arima"];

export function TimeSeriesClient() {
  const dataset = useAnalyticsStore((state) => state.dataset);
  const addResult = useAnalyticsStore((state) => state.addResult);
  const [method, setMethod] = useState<TimeSeriesMethodType>("linear_regression");
  const [result, setResult] = useState<TimeSeriesRunResponseDTO | null>(null);
  const [diagrams, setDiagrams] = useState<DiagramsResponseDTO | null>(null);

  const mutation = useMutation({
    mutationFn: async () => {
      if (!dataset) throw new Error("Upload a dataset first.");
      const output = await api.runTimeSeries({ upload_id: dataset.uploadId, method_type: method });
      const fetchedDiagrams = await api.getDiagrams(dataset.uploadId, "time_series").catch(() => null);
      return { output, fetchedDiagrams };
    },
    onSuccess: ({ output, fetchedDiagrams }) => {
      setResult(output);
      setDiagrams(fetchedDiagrams);
      addResult("time-series", {
        name: `Time Series: ${output.time_series_method_type}`,
        methodType: "time_series",
        params: { method_type: method },
        output,
        diagrams: fetchedDiagrams,
        createdAt: new Date().toISOString()
      });
      toast.success("Forecast generated", { description: `${titleCase(output.time_series_method_type)} returned forecast artifacts.` });
    },
    onError: (error) => toast.error("Forecast failed", { description: error instanceof Error ? error.message : "Try again." })
  });

  return (
    <AlgorithmGuard method="time_series">
      <div className="mx-auto max-w-7xl space-y-8">
        <div>
          <Badge variant="outline">Time Series</Badge>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight">Forecasting studio</h1>
          <p className="mt-2 max-w-2xl text-muted-foreground">Run linear regression or ARIMA forecasting, inspect trend charts, and collect plot artifacts.</p>
        </div>

        <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
          <Card className="bg-card/75 backdrop-blur-xl">
            <CardHeader>
              <CardTitle>Forecast method</CardTitle>
              <CardDescription>POST /time-series/run with selected method type.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {methods.map((item) => (
                <button key={item} onClick={() => setMethod(item)} className={`w-full rounded-2xl border p-4 text-left transition ${method === item ? "border-primary bg-primary/10" : "border-border bg-background/60 hover:bg-muted"}`}>
                  <p className="font-medium">{titleCase(item)}</p>
                  <p className="mt-1 text-xs text-muted-foreground">Use method_type = {item}</p>
                </button>
              ))}
              <Button className="w-full" variant="gradient" onClick={() => mutation.mutate()} disabled={mutation.isPending}>
                <LineChartIcon className="h-4 w-4" /> {mutation.isPending ? "Forecasting..." : "Run forecast"}
              </Button>
            </CardContent>
          </Card>

          <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-3">
              <MetricCard title="Target column" value={result?.target_column ?? "—"} icon={Target} />
              <MetricCard title="Datetime column" value={result?.datetime_column ?? "—"} icon={CalendarClock} />
              <MetricCard title="Metrics" value={result ? Object.keys(result.metrics).length : "—"} icon={Sigma} />
            </div>

            <Card className="bg-card/75 backdrop-blur-xl">
              <CardHeader>
                <CardTitle>Historical and forecast plot</CardTitle>
                <CardDescription>Polished forecast chart using realistic preview data until plot files are parsed.</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={forecastData}>
                      <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                      <XAxis dataKey="date" tickLine={false} axisLine={false} fontSize={12} />
                      <YAxis tickLine={false} axisLine={false} fontSize={12} />
                      <Tooltip contentStyle={{ borderRadius: 16, border: "1px solid hsl(var(--border))", background: "hsl(var(--card))" }} />
                      <Line type="monotone" dataKey="actual" stroke="currentColor" strokeWidth={3} dot={false} className="text-primary" />
                      <Line type="monotone" dataKey="predicted" stroke="currentColor" strokeWidth={3} strokeDasharray="6 6" dot={false} className="text-sky-500" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <Card className="bg-card/75 backdrop-blur-xl">
            <CardHeader>
              <CardTitle>Returned artifacts</CardTitle>
              <CardDescription>Paths and metrics from the forecasting response.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="rounded-2xl border border-border bg-background/60 p-4"><span className="font-semibold">Forecast file:</span> <span className="text-muted-foreground">{result?.forecast_file_path ?? "Pending"}</span></div>
              <div className="rounded-2xl border border-border bg-background/60 p-4"><span className="font-semibold">Historical plot:</span> <span className="text-muted-foreground">{result?.historical_plot_path ?? "Pending"}</span></div>
              <div className="rounded-2xl border border-border bg-background/60 p-4"><span className="font-semibold">Forecast plot:</span> <span className="text-muted-foreground">{result?.forecast_plot_path ?? "Pending"}</span></div>
              <pre className="max-h-64 overflow-auto rounded-2xl border border-border bg-slate-950 p-4 text-xs text-slate-100">{safeJsonStringify(result?.metrics ?? {})}</pre>
            </CardContent>
          </Card>
          <Card className="bg-card/75 backdrop-blur-xl">
            <CardHeader>
              <CardTitle>Generated diagrams</CardTitle>
              <CardDescription>Base64 time series diagrams with fullscreen previews.</CardDescription>
            </CardHeader>
            <CardContent><DiagramGallery diagrams={diagrams} /></CardContent>
          </Card>
        </div>
      </div>
    </AlgorithmGuard>
  );
}
