"use client";

import { useMutation } from "@tanstack/react-query";
import { Boxes, Hash, Radar } from "lucide-react";
import { useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { toast } from "sonner";
import { AlgorithmGuard } from "@/features/algorithms/algorithm-guard";
import { DiagramGallery } from "@/components/analytics/diagram-gallery";
import { MetricCard } from "@/components/analytics/metric-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/services/api";
import { useAnalyticsStore } from "@/store/session-store";
import type { BestClusteringRunResponseDTO, DiagramsResponseDTO } from "@/types/api";
import { titleCase } from "@/lib/utils";

export function ClusteringClient() {
  const dataset = useAnalyticsStore((state) => state.dataset);
  const addResult = useAnalyticsStore((state) => state.addResult);
  const [bestResult, setBestResult] = useState<BestClusteringRunResponseDTO | null>(null);
  const [diagrams, setDiagrams] = useState<DiagramsResponseDTO | null>(null);
  const insights = bestResult?.insights ?? null;

  const bestMutation = useMutation({
    mutationFn: async () => {
      if (!dataset) throw new Error("Upload a dataset first.");
      const result = await api.runBestClustering({ upload_id: dataset.uploadId });
      const fetchedDiagrams = await api.getDiagrams(dataset.uploadId, "clustering").catch(() => null);
      return { result, fetchedDiagrams };
    },
    onSuccess: ({ result, fetchedDiagrams }) => {
      setBestResult(result);
      setDiagrams(fetchedDiagrams);
      addResult("best-clustering", {
        name: "Best clustering comparison",
        methodType: "clustering",
        params: { mode: "best" },
        output: result,
        diagrams: fetchedDiagrams,
        createdAt: new Date().toISOString()
      });
      toast.success("Best clustering complete", { description: `${titleCase(result.best_algorithm)} performed best.` });
    },
    onError: (error) => toast.error("Comparison failed", { description: error instanceof Error ? error.message : "Try again." })
  });

  const comparisonData = useMemo(
    () => bestResult?.results.map((item) => ({ name: titleCase(item.algorithm), silhouette: item.silhouette, clusters: item.n_clusters })) ?? [],
    [bestResult]
  );
  const bestScore = useMemo(
    () => bestResult?.results.find((item) => item.algorithm === bestResult.best_algorithm) ?? null,
    [bestResult]
  );

  return (
    <AlgorithmGuard method="clustering">
      <div className="mx-auto max-w-7xl space-y-8">
        <div>
          <Badge variant="outline">Clustering</Badge>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight">Cluster discovery studio</h1>
          <p className="mt-2 max-w-2xl text-muted-foreground">Run all clustering methods, select the best result automatically, and inspect generated diagrams.</p>
        </div>

        <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
          <Card className="bg-card/75 backdrop-blur-xl">
            <CardHeader>
              <CardTitle>Automatic best clustering</CardTitle>
              <CardDescription>POST /clustering/best runs all methods and returns the top performer.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-2xl border border-border bg-background/60 p-4 text-sm text-muted-foreground">
                Run the workflow once. The system compares methods and returns the best clustering output.
              </div>
              <Button className="w-full" variant="gradient" onClick={() => bestMutation.mutate()} disabled={bestMutation.isPending}>
                {bestMutation.isPending ? "Comparing..." : "Run best clustering"}
              </Button>
            </CardContent>
          </Card>

          <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-3">
              <MetricCard title="Clusters" value={bestScore?.n_clusters ?? "—"} icon={Boxes} />
              <MetricCard title="Noise points" value={bestScore?.noise_points ?? "—"} icon={Radar} />
              <MetricCard title="Best method" value={bestResult ? titleCase(bestResult.best_algorithm) : "—"} icon={Hash} />
            </div>

            <Card className="bg-card/75 backdrop-blur-xl">
              <CardHeader>
                <CardTitle>Best algorithm comparison</CardTitle>
                <CardDescription>Silhouette scores returned by POST /clustering/best.</CardDescription>
              </CardHeader>
              <CardContent>
                {comparisonData.length ? (
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={comparisonData}>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                        <XAxis dataKey="name" tickLine={false} axisLine={false} fontSize={12} />
                        <YAxis tickLine={false} axisLine={false} fontSize={12} />
                        <Tooltip contentStyle={{ borderRadius: 16, border: "1px solid hsl(var(--border))", background: "hsl(var(--card))" }} />
                        <Bar dataKey="silhouette" radius={[12, 12, 0, 0]} fill="currentColor" className="text-primary" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="rounded-2xl border border-dashed border-border bg-background/60 p-6 text-sm text-muted-foreground">
                    Run clustering to compare methods and view scores.
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        <Card className="bg-card/75 backdrop-blur-xl">
          <CardHeader>
            <CardTitle>Generated diagrams</CardTitle>
            <CardDescription>Base64 images from GET /files/diagrams/{'{upload_id}'}/clustering.</CardDescription>
          </CardHeader>
          <CardContent>
            <DiagramGallery diagrams={diagrams} />
          </CardContent>
        </Card>

        <Card className="bg-card/75 backdrop-blur-xl">
          <CardHeader>
            <CardTitle>Insights</CardTitle>
            <CardDescription>Plain-language clustering highlights.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            {insights?.length ? insights.map((item, index) => (
              <div key={index} className="rounded-2xl border border-border bg-background/60 p-3">{item}</div>
            )) : <p>No insights yet. Run clustering to generate summaries.</p>}
          </CardContent>
        </Card>
      </div>
    </AlgorithmGuard>
  );
}
