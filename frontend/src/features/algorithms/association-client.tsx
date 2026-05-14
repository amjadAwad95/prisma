"use client";

import { useMutation } from "@tanstack/react-query";
import { Network, Ratio, Sparkles, TableProperties } from "lucide-react";
import { useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
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
import type { AssociationRunResponseDTO, DiagramsResponseDTO } from "@/types/api";
import { associationRules } from "@/utils/demo-data";

export function AssociationClient() {
  const dataset = useAnalyticsStore((state) => state.dataset);
  const addResult = useAnalyticsStore((state) => state.addResult);
  const [minSupport, setMinSupport] = useState(0.2);
  const [minConfidence, setMinConfidence] = useState(0.6);
  const [minLift, setMinLift] = useState(1.1);
  const [result, setResult] = useState<AssociationRunResponseDTO | null>(null);
  const [diagrams, setDiagrams] = useState<DiagramsResponseDTO | null>(null);

  const mutation = useMutation({
    mutationFn: async () => {
      if (!dataset) throw new Error("Upload a dataset first.");
      const output = await api.runAssociation({
        upload_id: dataset.uploadId,
        min_support: minSupport,
        min_confidence: minConfidence,
        min_lift: minLift
      });
      const fetchedDiagrams = await api.getDiagrams(dataset.uploadId, "association").catch(() => null);
      return { output, fetchedDiagrams };
    },
    onSuccess: ({ output, fetchedDiagrams }) => {
      setResult(output);
      setDiagrams(fetchedDiagrams);
      addResult("association", {
        name: "Association Rule Mining",
        methodType: "association_rule",
        params: { min_support: minSupport, min_confidence: minConfidence, min_lift: minLift },
        output,
        diagrams: fetchedDiagrams,
        createdAt: new Date().toISOString()
      });
      toast.success("Association mining complete", { description: "Frequent itemsets and rules paths were returned." });
    },
    onError: (error) => toast.error("Association mining failed", { description: error instanceof Error ? error.message : "Try again." })
  });

  return (
    <AlgorithmGuard method="association_rule">
      <div className="mx-auto max-w-7xl space-y-8">
        <div>
          <Badge variant="outline">Association Rule Mining</Badge>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight">Rule discovery console</h1>
          <p className="mt-2 max-w-2xl text-muted-foreground">Find frequent itemsets, tune support/confidence/lift thresholds, and render rule visualizations.</p>
        </div>

        <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
          <Card className="bg-card/75 backdrop-blur-xl">
            <CardHeader>
              <CardTitle>Threshold controls</CardTitle>
              <CardDescription>POST /association/run with minimum support, confidence, and lift.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              <label className="grid gap-2 text-sm font-medium">Min support <Input type="number" step="0.01" min="0" max="1" value={minSupport} onChange={(event) => setMinSupport(Number(event.target.value))} /></label>
              <label className="grid gap-2 text-sm font-medium">Min confidence <Input type="number" step="0.01" min="0" max="1" value={minConfidence} onChange={(event) => setMinConfidence(Number(event.target.value))} /></label>
              <label className="grid gap-2 text-sm font-medium">Min lift <Input type="number" step="0.1" min="0" value={minLift} onChange={(event) => setMinLift(Number(event.target.value))} /></label>
              <Button className="w-full" variant="gradient" onClick={() => mutation.mutate()} disabled={mutation.isPending}>
                <Network className="h-4 w-4" /> {mutation.isPending ? "Mining rules..." : "Run association mining"}
              </Button>
            </CardContent>
          </Card>

          <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-3">
              <MetricCard title="Min support" value={minSupport} icon={Sparkles} />
              <MetricCard title="Min confidence" value={minConfidence} icon={Ratio} />
              <MetricCard title="Rule files" value={result ? "2" : "—"} icon={TableProperties} />
            </div>

            <Card className="bg-card/75 backdrop-blur-xl">
              <CardHeader>
                <CardTitle>Rule confidence and lift</CardTitle>
                <CardDescription>Interactive table and chart. Replace mock preview with parsed API output when file contents are exposed.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={associationRules.map((item) => ({ name: item.antecedent, confidence: item.confidence, lift: item.lift }))}>
                      <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                      <XAxis dataKey="name" tickLine={false} axisLine={false} fontSize={12} />
                      <YAxis tickLine={false} axisLine={false} fontSize={12} />
                      <Tooltip contentStyle={{ borderRadius: 16, border: "1px solid hsl(var(--border))", background: "hsl(var(--card))" }} />
                      <Bar dataKey="confidence" radius={[10, 10, 0, 0]} fill="currentColor" className="text-primary" />
                      <Bar dataKey="lift" radius={[10, 10, 0, 0]} fill="currentColor" className="text-sky-500" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="overflow-x-auto rounded-2xl border border-border">
                  <table className="w-full text-sm">
                    <thead className="bg-muted text-left text-xs uppercase text-muted-foreground">
                      <tr><th className="px-4 py-3">Antecedent</th><th className="px-4 py-3">Consequent</th><th className="px-4 py-3">Confidence</th><th className="px-4 py-3">Lift</th></tr>
                    </thead>
                    <tbody>
                      {associationRules.map((rule) => (
                        <tr key={rule.antecedent} className="border-t border-border">
                          <td className="px-4 py-3">{rule.antecedent}</td>
                          <td className="px-4 py-3 text-muted-foreground">{rule.consequent}</td>
                          <td className="px-4 py-3">{rule.confidence}</td>
                          <td className="px-4 py-3">{rule.lift}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-2">
          <Card className="bg-card/75 backdrop-blur-xl">
            <CardHeader>
              <CardTitle>Output files</CardTitle>
              <CardDescription>Paths returned by the API.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="rounded-2xl border border-border bg-background/60 p-4"><span className="font-semibold">Frequent itemsets:</span> <span className="text-muted-foreground">{result?.frequent_itemsets_file_path ?? "Pending"}</span></div>
              <div className="rounded-2xl border border-border bg-background/60 p-4"><span className="font-semibold">Association rules:</span> <span className="text-muted-foreground">{result?.association_rules_file_path ?? "Pending"}</span></div>
            </CardContent>
          </Card>
          <Card className="bg-card/75 backdrop-blur-xl">
            <CardHeader>
              <CardTitle>Generated diagrams</CardTitle>
              <CardDescription>Base64 rule diagrams from the diagrams endpoint.</CardDescription>
            </CardHeader>
            <CardContent><DiagramGallery diagrams={diagrams} /></CardContent>
          </Card>
        </div>
      </div>
    </AlgorithmGuard>
  );
}
