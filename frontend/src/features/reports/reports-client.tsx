"use client";

import { useMutation } from "@tanstack/react-query";
import { Download, FileText, Printer, Wand2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { EmptyState } from "@/components/feedback/empty-state";
import { MarkdownReportViewer } from "@/components/analytics/markdown-report-viewer";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/services/api";
import { useAnalyticsStore } from "@/store/session-store";
import type { AlgorithmReportInputDTO, DatasetSession, MethodType, ReportResponseDTO, UploadResponseDTO } from "@/types/api";
import { downloadTextFile } from "@/lib/utils";

const fallbackReport = `# Smart Analytics Report\n\nUpload a dataset and run one or more algorithms to generate a complete markdown report.\n\n## What will be included\n\n- Dataset upload ID and metadata\n- Algorithm parameters\n- Measures and outputs\n- Diagram artifacts and notes\n- Recommendations and next steps\n`;

export function ReportsClient() {
  const dataset = useAnalyticsStore((state) => state.dataset);
  const history = useAnalyticsStore((state) => state.history);
  const resultsBySession = useAnalyticsStore((state) => state.resultsBySession);
  const setHistory = useAnalyticsStore((state) => state.setHistory);
  const setActiveSession = useAnalyticsStore((state) => state.setActiveSession);
  const setAllowedMethods = useAnalyticsStore((state) => state.setAllowedMethods);
  const [report, setReport] = useState<ReportResponseDTO | null>(null);

  useEffect(() => {
    let isActive = true;
    api.listMetadata()
      .then((uploads) => {
        if (!isActive) return;
        const currentHistory = useAnalyticsStore.getState().history;
        if (!uploads.length) return;
        setHistory(mergeHistory(currentHistory, uploads));
      })
      .catch(() => undefined);
    return () => {
      isActive = false;
    };
  }, [setHistory]);

  const sessionResults = dataset ? resultsBySession[dataset.uploadId] ?? {} : {};

  const algorithms = useMemo<AlgorithmReportInputDTO[]>(() => {
    const results = Object.values(sessionResults);
    const bestClustering = results.find((item) => item.methodType === "clustering" && (item.params as { mode?: string } | undefined)?.mode === "best")
      ?? results.find((item) => item.methodType === "clustering" && item.name.toLowerCase().includes("best"))
      ?? null;

    return results
      .filter((item) => item.methodType !== "clustering" || item === bestClustering)
      .map((result) => ({
        name: result.name,
        params: result.params,
        outputs: result.output as Record<string, unknown>,
        measures: result.output as Record<string, unknown>,
        notes: result.diagrams?.images?.length ? `${result.diagrams.images.length} diagrams attached.` : undefined
      }));
  }, [sessionResults]);

  const mutation = useMutation({
    mutationFn: async () => {
      if (!dataset) throw new Error("Upload a dataset before generating a report.");
      if (!algorithms.length) throw new Error("Run at least one algorithm for this session first.");
      return api.generateReport({ upload_id: dataset.uploadId, algorithms });
    },
    onSuccess: (output) => {
      setReport(output);
      toast.success("Report generated", { description: "Markdown is ready for review and export." });
    },
    onError: (error) => toast.error("Report generation failed", { description: error instanceof Error ? error.message : "Try again." })
  });

  const markdown = report?.report_text ?? fallbackReport;

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <Badge variant="outline">Reports</Badge>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight">Intelligent analysis reports</h1>
          <p className="mt-2 max-w-2xl text-muted-foreground">Generate a report for the selected dataset session, then export to markdown or browser PDF.</p>
        </div>
        <div className="flex flex-wrap gap-2 no-print">
          <Button variant="gradient" onClick={() => mutation.mutate()} disabled={mutation.isPending || !dataset || !algorithms.length}>
            <Wand2 className="h-4 w-4" /> {mutation.isPending ? "Generating..." : "Generate report"}
          </Button>
          <Button variant="outline" onClick={() => downloadTextFile("smart-analytics-report.md", markdown)}>
            <Download className="h-4 w-4" /> Markdown
          </Button>
          <Button variant="outline" onClick={() => window.print()}>
            <Printer className="h-4 w-4" /> PDF / Print
          </Button>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[340px_1fr]">
        <Card className="no-print h-fit bg-card/75 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><FileText className="h-4 w-4" /> Report inputs</CardTitle>
            <CardDescription>Data sent to POST /reports/generate.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-2xl border border-border bg-background/60 p-4">
              <p className="text-xs uppercase text-muted-foreground">Session</p>
              <select
                className="mt-2 w-full rounded-xl border border-border bg-background/60 px-3 py-2 text-sm"
                value={dataset?.uploadId ?? ""}
                onChange={async (event) => {
                  const uploadId = event.target.value;
                  if (!uploadId) return;
                  setActiveSession(uploadId);
                  const selected = history.find((item) => item.uploadId === uploadId);
                  if (selected?.methodTypes?.length) {
                    setAllowedMethods(selected.methodTypes);
                    return;
                  }
                  const allowed = await api.getAllowedMethods(uploadId).catch(() => null);
                  if (allowed?.method_type?.length) {
                    setAllowedMethods(allowed.method_type as MethodType[]);
                  }
                }}
              >
                <option value="" disabled>Select a session</option>
                {history.map((item) => (
                  <option key={item.uploadId} value={item.uploadId}>{item.filename}</option>
                ))}
              </select>
              <p className="mt-2 truncate font-mono text-xs text-muted-foreground">{dataset?.uploadId ?? "No dataset selected"}</p>
            </div>
            <div className="rounded-2xl border border-border bg-background/60 p-4">
              <p className="text-xs uppercase text-muted-foreground">Algorithms included</p>
              <p className="mt-1 text-2xl font-semibold">{algorithms.length}</p>
            </div>
            <div className="space-y-2">
              {algorithms.length ? algorithms.map((item) => (
                <div key={item.name} className="rounded-2xl border border-border bg-background/60 p-3 text-sm">{item.name}</div>
              )) : <p className="text-sm text-muted-foreground">No algorithm outputs in session yet.</p>}
            </div>
          </CardContent>
        </Card>

        {dataset && algorithms.length ? <MarkdownReportViewer markdown={markdown} /> : <EmptyState title="Run analysis first" description="Reports are generated by collecting algorithm outputs from the selected session." />}
      </div>
    </div>
  );
}

function normalizeMethods(input?: string[] | null): MethodType[] {
  const allowed: MethodType[] = ["clustering", "association_rule", "time_series"];
  return (input ?? []).filter((item): item is MethodType => allowed.includes(item as MethodType));
}

function mergeHistory(existing: DatasetSession[], uploads: UploadResponseDTO[]): DatasetSession[] {
  const mergedMap = new Map(existing.map((item) => [item.uploadId, item]));
  uploads.forEach((upload) => {
    const saved = mergedMap.get(upload.upload_id);
    const fallbackMethods = normalizeMethods(upload.method_types);
    const methodTypes = saved?.methodTypes?.length
      ? saved.methodTypes
      : fallbackMethods.length
        ? fallbackMethods
        : ["clustering", "association_rule", "time_series"];
    mergedMap.set(upload.upload_id, {
      uploadId: upload.upload_id,
      filename: upload.filename,
      bytes: upload.bytes,
      contentType: upload.content_type,
      uploadedAt: saved?.uploadedAt ?? new Date().toISOString(),
      methodTypes,
      metadata: saved?.metadata ?? { path: upload.path }
    } satisfies DatasetSession);
  });

  return Array.from(mergedMap.values())
    .sort((a, b) => new Date(b.uploadedAt).getTime() - new Date(a.uploadedAt).getTime())
    .slice(0, 12);
}
