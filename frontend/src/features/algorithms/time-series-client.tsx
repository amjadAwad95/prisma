"use client";

import { useMutation } from "@tanstack/react-query";
import { CalendarClock, LineChart as LineChartIcon, Sigma, Target } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { AlgorithmGuard } from "@/features/algorithms/algorithm-guard";
import { DiagramGallery } from "@/components/analytics/diagram-gallery";
import { MetricCard } from "@/components/analytics/metric-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/services/api";
import { useAnalyticsStore } from "@/store/session-store";
import type { DiagramsResponseDTO, TimeSeriesRunResponseDTO } from "@/types/api";
import { titleCase } from "@/lib/utils";

export function TimeSeriesClient() {
  const dataset = useAnalyticsStore((state) => state.dataset);
  const addResult = useAnalyticsStore((state) => state.addResult);
  const [result, setResult] = useState<TimeSeriesRunResponseDTO | null>(null);
  const [diagrams, setDiagrams] = useState<DiagramsResponseDTO | null>(null);

  const mutation = useMutation({
    mutationFn: async () => {
      if (!dataset) throw new Error("Upload a dataset first.");
      const output = await api.runTimeSeries({ upload_id: dataset.uploadId });
      const fetchedDiagrams = await api.getDiagrams(dataset.uploadId, "time_series").catch(() => null);
      return { output, fetchedDiagrams };
    },
    onSuccess: ({ output, fetchedDiagrams }) => {
      setResult(output);
      setDiagrams(fetchedDiagrams);
      addResult("time-series", {
        name: "Time Series Forecast",
        methodType: "time_series",
        params: { mode: "auto" },
        output,
        diagrams: fetchedDiagrams,
        createdAt: new Date().toISOString()
      });
      toast.success("Forecast generated", { description: `${titleCase(output.time_series_method_type)} produced a new forecast.` });
    },
    onError: (error) => toast.error("Forecast failed", { description: error instanceof Error ? error.message : "Try again." })
  });

  return (
    <AlgorithmGuard method="time_series">
      <div className="mx-auto max-w-7xl space-y-8">
        <div>
          <Badge variant="outline">Time Series</Badge>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight">Forecasting studio</h1>
          <p className="mt-2 max-w-2xl text-muted-foreground">Forecasting runs automatically with the best method and summarizes what changed.</p>
        </div>

        <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
          <Card className="bg-card/75 backdrop-blur-xl">
            <CardHeader>
              <CardTitle>Forecasting</CardTitle>
              <CardDescription>Forecasting using ARIMA.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-2xl border border-border bg-background/60 p-4 text-sm text-muted-foreground">
                Upload a dataset and run the workflow. The system chooses the best forecasting method automatically.
              </div>
              <Button className="w-full" variant="gradient" onClick={() => mutation.mutate()} disabled={mutation.isPending}>
                <LineChartIcon className="h-4 w-4" /> {mutation.isPending ? "Forecasting..." : "Run forecast"}
              </Button>
            </CardContent>
          </Card>

          <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-3">
              <MetricCard title="Target column" value={result?.target_column ?? "—"} icon={Target} />
              <MetricCard title="Datetime column" value={result?.datetime_column ?? "—"} icon={CalendarClock} />
              {/* <MetricCard title="Metrics" value={result ? Object.keys(result.metrics).length : "—"} icon={Sigma} /> */}
            </div>

          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <Card className="bg-card/75 backdrop-blur-xl">
            <CardHeader>
              <CardTitle>Insights</CardTitle>
              <CardDescription>What your time series is showing.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-muted-foreground">
              {result?.insights?.length ? result.insights.map((item, index) => (
                <div key={index} className="rounded-2xl border border-border bg-background/60 p-3">{item}</div>
              )) : <p>No insights yet. Run forecasting to generate summaries.</p>}
            </CardContent>
          </Card>
          <Card className="bg-card/75 backdrop-blur-xl">
            <CardHeader>
              <CardTitle>Generated diagrams</CardTitle>
              <CardDescription>Charts generated from your time series model.</CardDescription>
            </CardHeader>
            <CardContent><DiagramGallery diagrams={diagrams} /></CardContent>
          </Card>
        </div>
      </div>
    </AlgorithmGuard>
  );
}
