"use client";

import { useMutation } from "@tanstack/react-query";
import { Boxes, GitCompareArrows, Hash, Radar, ScanSearch } from "lucide-react";
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
import type { BestClusteringRunResponseDTO, ClusteringAlgorithm, ClusteringRunResponseDTO, DiagramsResponseDTO } from "@/types/api";
import { titleCase } from "@/lib/utils";

const algorithms: ClusteringAlgorithm[] = ["kmeans", "dbscan", "hierarchical"];

export function ClusteringClient() {
  const dataset = useAnalyticsStore((state) => state.dataset);
  const addResult = useAnalyticsStore((state) => state.addResult);
  const [algorithm, setAlgorithm] = useState<ClusteringAlgorithm>("kmeans");
  const [runResult, setRunResult] = useState<ClusteringRunResponseDTO | null>(null);
  const [bestResult, setBestResult] = useState<BestClusteringRunResponseDTO | null>(null);
  const [diagrams, setDiagrams] = useState<DiagramsResponseDTO | null>(null);

  const runMutation = useMutation({
    mutationFn: async () => {
      if (!dataset) throw new Error("Upload a dataset first.");
      const result = await api.runClustering({ upload_id: dataset.uploadId, algorithm });
      const fetchedDiagrams = await api.getDiagrams(dataset.uploadId, "clustering").catch(() => null);
      return { result, fetchedDiagrams };
    },
    onSuccess: ({ result, fetchedDiagrams }) => {
      setRunResult(result);
      setDiagrams(fetchedDiagrams);
      addResult("clustering", {
        name: `Clustering: ${result.algorithm}`,
        methodType: "clustering",
        params: { algorithm: result.algorithm },
        output: result,
        diagrams: fetchedDiagrams,
        createdAt: new Date().toISOString()
      });
      toast.success("Clustering completed", { description: `${titleCase(result.algorithm)} found ${result.n_clusters} clusters.` });
    },
    onError: (error) => toast.error("Clustering failed", { description: error instanceof Error ? error.message : "Try again." })
  });

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
      toast.success("Best clustering comparison complete", { description: `${titleCase(result.best_algorithm)} performed best.` });
    },
    onError: (error) => toast.error("Comparison failed", { description: error instanceof Error ? error.message : "Try again." })
  });

  const comparisonData = useMemo(() => bestResult?.results.map((item) => ({ name: titleCase(item.algorithm), silhouette: item.silhouette, clusters: item.n_clusters })) ?? [], [bestResult]);

  return (
    <AlgorithmGuard method="clustering">
      <div className="mx-auto max-w-7xl space-y-8">
        <div>
          <Badge variant="outline">Clustering</Badge>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight">Cluster discovery studio</h1>
          <p className="mt-2 max-w-2xl text-muted-foreground">Run KMeans, DBSCAN, or hierarchical clustering, compare the best algorithm, and inspect generated diagrams.</p>
        </div>

        <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
          <Card className="bg-card/75 backdrop-blur-xl">
            <CardHeader>
              <CardTitle>Parameters</CardTitle>
              <CardDescription>Select a clustering method and execute the API workflow.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-3">
                {algorithms.map((item) => (
                  <button key={item} onClick={() => setAlgorithm(item)} className={`rounded-2xl border p-4 text-left transition ${algorithm === item ? "border-primary bg-primary/10" : "border-border bg-background/60 hover:bg-muted"}`}>
                    <p className="font-medium">{titleCase(item)}</p>
                    <p className="mt-1 text-xs text-muted-foreground">Run POST /clustering/run with algorithm = {item}.</p>
                  </button>
                ))}
              </div>
              <Button className="w-full" variant="gradient" onClick={() => runMutation.mutate()} disabled={runMutation.isPending}>
                <ScanSearch className="h-4 w-4" /> {runMutation.isPending ? "Running..." : "Run clustering"}
              </Button>
              <Button className="w-full" variant="outline" onClick={() => bestMutation.mutate()} disabled={bestMutation.isPending}>
                <GitCompareArrows className="h-4 w-4" /> {bestMutation.isPending ? "Comparing..." : "Find best clustering"}
              </Button>
            </CardContent>
          </Card>

          <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-3">
              <MetricCard title="Clusters" value={runResult?.n_clusters ?? bestResult?.results?.[0]?.n_clusters ?? "—"} icon={Boxes} />
              <MetricCard title="Noise points" value={runResult?.noise_points ?? "—"} icon={Radar} />
              <MetricCard title="Best method" value={bestResult ? titleCase(bestResult.best_algorithm) : "—"} icon={Hash} />
            </div>

            <Card className="bg-card/75 backdrop-blur-xl">
              <CardHeader>
                <CardTitle>Best algorithm comparison</CardTitle>
                <CardDescription>Silhouette scores returned by POST /clustering/best.</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={comparisonData.length ? comparisonData : [{ name: "KMeans", silhouette: 0.62 }, { name: "DBSCAN", silhouette: 0.48 }, { name: "Hierarchical", silhouette: 0.58 }]}>
                      <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                      <XAxis dataKey="name" tickLine={false} axisLine={false} fontSize={12} />
                      <YAxis tickLine={false} axisLine={false} fontSize={12} />
                      <Tooltip contentStyle={{ borderRadius: 16, border: "1px solid hsl(var(--border))", background: "hsl(var(--card))" }} />
                      <Bar dataKey="silhouette" radius={[12, 12, 0, 0]} fill="currentColor" className="text-primary" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
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
      </div>
    </AlgorithmGuard>
  );
}
