"use client";

import { useMutation } from "@tanstack/react-query";
import { Activity, Layers3, Percent, SlidersHorizontal } from "lucide-react";
import { useMemo, useState } from "react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { toast } from "sonner";
import { AlgorithmGuard } from "@/features/algorithms/algorithm-guard";
import { DiagramGallery } from "@/components/analytics/diagram-gallery";
import { MetricCard } from "@/components/analytics/metric-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/services/api";
import { useAnalyticsStore } from "@/store/session-store";
import type { DiagramsResponseDTO, PCARunResponseDTO } from "@/types/api";
import { varianceData } from "@/utils/demo-data";

export function PCAClient() {
  const dataset = useAnalyticsStore((state) => state.dataset);
  const addResult = useAnalyticsStore((state) => state.addResult);
  const [nComponents, setNComponents] = useState(0.95);
  const [threshold, setThreshold] = useState(0.95);
  const [result, setResult] = useState<PCARunResponseDTO | null>(null);
  const [diagrams, setDiagrams] = useState<DiagramsResponseDTO | null>(null);

  const mutation = useMutation({
    mutationFn: async () => {
      if (!dataset) throw new Error("Upload a dataset first.");
      const output = await api.runPCA({ upload_id: dataset.uploadId, n_components: nComponents, threshold });
      const fetchedDiagrams = await api.getDiagrams(dataset.uploadId, "pca").catch(() => null);
      return { output, fetchedDiagrams };
    },
    onSuccess: ({ output, fetchedDiagrams }) => {
      setResult(output);
      setDiagrams(fetchedDiagrams);
      addResult("pca", {
        name: "Principal Component Analysis",
        methodType: "pca",
        params: { n_components: nComponents, threshold },
        output,
        diagrams: fetchedDiagrams,
        createdAt: new Date().toISOString()
      });
      toast.success("PCA completed", { description: `${output.pca_method_type} returned ${output.explained_variance_ratio.length} variance components.` });
    },
    onError: (error) => toast.error("PCA failed", { description: error instanceof Error ? error.message : "Try again." })
  });

  const chartData = useMemo(() => {
    if (!result) return varianceData;
    return result.explained_variance_ratio.map((variance, index) => ({
      component: `PC${index + 1}`,
      variance,
      cumulative: Number(result.cumulative_variance[index] ?? 0)
    }));
  }, [result]);

  return (
    <AlgorithmGuard method="pca">
      <div className="mx-auto max-w-7xl space-y-8">
        <div>
          <Badge variant="outline">PCA</Badge>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight">Dimensionality reduction lab</h1>
          <p className="mt-2 max-w-2xl text-muted-foreground">Tune component and threshold controls, inspect explained variance, and preview transformed outputs.</p>
        </div>

        <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
          <Card className="bg-card/75 backdrop-blur-xl">
            <CardHeader>
              <CardTitle>Controls</CardTitle>
              <CardDescription>POST /pca/run accepts upload ID, component count, and variance threshold.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              <label className="grid gap-2 text-sm font-medium">
                Components / variance ratio
                <Input type="number" step="0.05" min="0.1" max="20" value={nComponents} onChange={(event) => setNComponents(Number(event.target.value))} />
              </label>
              <label className="grid gap-2 text-sm font-medium">
                Threshold
                <Input type="number" step="0.01" min="0.1" max="1" value={threshold} onChange={(event) => setThreshold(Number(event.target.value))} />
              </label>
              <Button className="w-full" variant="gradient" onClick={() => mutation.mutate()} disabled={mutation.isPending}>
                <SlidersHorizontal className="h-4 w-4" /> {mutation.isPending ? "Running PCA..." : "Run PCA"}
              </Button>
            </CardContent>
          </Card>

          <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-3">
              <MetricCard title="Method" value={result?.pca_method_type ?? "—"} icon={Layers3} />
              <MetricCard title="Components" value={result?.explained_variance_ratio.length ?? "—"} icon={Activity} />
              <MetricCard title="Cumulative variance" value={result ? `${Math.round(Number(result.cumulative_variance.at(-1) ?? 0) * 100)}%` : "—"} icon={Percent} />
            </div>

            <Card className="bg-card/75 backdrop-blur-xl">
              <CardHeader>
                <CardTitle>Scree and cumulative variance</CardTitle>
                <CardDescription>Animated chart from explained_variance_ratio and cumulative_variance arrays.</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                      <XAxis dataKey="component" tickLine={false} axisLine={false} fontSize={12} />
                      <YAxis tickLine={false} axisLine={false} fontSize={12} />
                      <Tooltip contentStyle={{ borderRadius: 16, border: "1px solid hsl(var(--border))", background: "hsl(var(--card))" }} />
                      <Bar dataKey="variance" radius={[10, 10, 0, 0]} fill="currentColor" className="text-primary" />
                      <Line type="monotone" dataKey="cumulative" stroke="currentColor" strokeWidth={3} className="text-sky-500" dot={false} />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <Card className="bg-card/75 backdrop-blur-xl">
            <CardHeader>
              <CardTitle>Transformed dataset preview</CardTitle>
              <CardDescription>{result?.transformed_data_file_path ?? "Run PCA to receive the transformed data path."}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                    <XAxis dataKey="component" tickLine={false} axisLine={false} fontSize={12} />
                    <YAxis tickLine={false} axisLine={false} fontSize={12} />
                    <Tooltip contentStyle={{ borderRadius: 16, border: "1px solid hsl(var(--border))", background: "hsl(var(--card))" }} />
                    <Area type="monotone" dataKey="cumulative" stroke="currentColor" fill="currentColor" fillOpacity={0.12} strokeWidth={3} className="text-primary" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-card/75 backdrop-blur-xl">
            <CardHeader>
              <CardTitle>Generated diagrams</CardTitle>
              <CardDescription>Base64 PCA diagrams are rendered with lazy loading and fullscreen preview.</CardDescription>
            </CardHeader>
            <CardContent>
              <DiagramGallery diagrams={diagrams} />
            </CardContent>
          </Card>
        </div>
      </div>
    </AlgorithmGuard>
  );
}
