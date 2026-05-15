"use client";

import { useMutation } from "@tanstack/react-query";
import { Network, Ratio, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { AlgorithmGuard } from "@/features/algorithms/algorithm-guard";
import { MetricCard } from "@/components/analytics/metric-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/services/api";
import { useAnalyticsStore } from "@/store/session-store";
import type { AssociationRunResponseDTO } from "@/types/api";

export function AssociationClient() {
  const dataset = useAnalyticsStore((state) => state.dataset);
  const addResult = useAnalyticsStore((state) => state.addResult);
  const [result, setResult] = useState<AssociationRunResponseDTO | null>(null);
  const [visibleRules, setVisibleRules] = useState(5);

  useEffect(() => {
    setVisibleRules(5);
  }, [result]);

  const availableRules = result?.rules ?? [];

  const ruleRows = useMemo(
    () => availableRules.slice(0, visibleRules),
    [availableRules, visibleRules]
  );

  const mutation = useMutation({
    mutationFn: async () => {
      if (!dataset) throw new Error("Upload a dataset first.");
      const output = await api.runAssociation({
        upload_id: dataset.uploadId
      });
      return { output };
    },
    onSuccess: ({ output }) => {
      setResult(output);
      addResult("association", {
        name: "Association Rule Mining",
        methodType: "association_rule",
        params: {
          min_support: output.min_support,
          min_confidence: output.min_confidence,
          min_lift: output.min_lift
        },
        output,
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
          <p className="mt-2 max-w-2xl text-muted-foreground">Find frequent itemsets with automatically selected thresholds and preview rule relationships.</p>
        </div>

        <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
          <Card className="bg-card/75 backdrop-blur-xl">
            <CardHeader>
              <CardTitle>Automatic thresholds</CardTitle>
              <CardDescription>POST /association/run chooses the best support, confidence, and lift for you.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="rounded-2xl border border-border bg-background/60 p-4 text-sm text-muted-foreground">
                Upload a dataset and run the workflow. The system finds the best thresholds automatically.
              </div>
              <Button className="w-full" variant="gradient" onClick={() => mutation.mutate()} disabled={mutation.isPending}>
                <Network className="h-4 w-4" /> {mutation.isPending ? "Mining rules..." : "Run association mining"}
              </Button>
            </CardContent>
          </Card>

          <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <MetricCard title="Min support" value={result?.min_support ?? "—"} icon={Sparkles} />
              <MetricCard title="Min confidence" value={result?.min_confidence ?? "—"} icon={Ratio} />
            </div>

            <Card className="bg-card/75 backdrop-blur-xl">
              <CardHeader>
                <CardTitle>Top association rules</CardTitle>
                <CardDescription>Showing simple item relationships. Load more to see additional rules.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {ruleRows.length ? (
                  <div className="space-y-2">
                    {ruleRows.map((rule) => (
                      <div key={`${rule.antecedent}-${rule.consequent}`} className="rounded-2xl border border-border bg-background/60 p-3 text-sm text-muted-foreground">
                        <span className="font-semibold text-foreground">{rule.antecedent}</span> → <span>{rule.consequent}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="rounded-2xl border border-dashed border-border bg-background/60 p-6 text-sm text-muted-foreground">
                    No rules yet. Run association mining to generate them.
                  </div>
                )}
                {availableRules.length > 0 ? (
                  <div className="flex justify-end">
                    <Button
                      variant="outline"
                      onClick={() => setVisibleRules((count) => count + 5)}
                      disabled={visibleRules >= availableRules.length}
                    >
                      Load more
                    </Button>
                  </div>
                ) : null}
              </CardContent>
            </Card>
          </div>
        </div>

        <Card className="bg-card/75 backdrop-blur-xl">
          <CardHeader>
            <CardTitle>Insights</CardTitle>
            <CardDescription>Plain-language co-purchase suggestions.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            {result?.insights?.length ? result.insights.map((item, index) => (
              <div key={index} className="rounded-2xl border border-border bg-background/60 p-3">{item}</div>
            )) : <p>No insights yet. Run association mining to generate suggestions.</p>}
          </CardContent>
        </Card>
      </div>
    </AlgorithmGuard>
  );
}
