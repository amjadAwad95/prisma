"use client";

import { useMutation } from "@tanstack/react-query";
import { Download, FileText, Printer, Wand2 } from "lucide-react";
import { useMemo, useState } from "react";
import { toast } from "sonner";
import { EmptyState } from "@/components/feedback/empty-state";
import { MarkdownReportViewer } from "@/components/analytics/markdown-report-viewer";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/services/api";
import { useAnalyticsStore } from "@/store/session-store";
import type { AlgorithmReportInputDTO, ReportResponseDTO } from "@/types/api";
import { downloadTextFile } from "@/lib/utils";

const fallbackReport = `# Smart Analytics Report\n\nUpload a dataset and run one or more algorithms to generate a complete markdown report.\n\n## What will be included\n\n- Dataset upload ID and metadata\n- Algorithm parameters\n- Measures and outputs\n- Diagram artifacts and notes\n- Recommendations and next steps\n`;

export function ReportsClient() {
  const dataset = useAnalyticsStore((state) => state.dataset);
  const results = useAnalyticsStore((state) => state.results);
  const [report, setReport] = useState<ReportResponseDTO | null>(null);

  const algorithms = useMemo<AlgorithmReportInputDTO[]>(() => {
    return Object.values(results).map((result) => ({
      name: result.name,
      params: result.params,
      outputs: result.output as Record<string, unknown>,
      measures: result.output as Record<string, unknown>,
      notes: result.diagrams?.images?.length ? `${result.diagrams.images.length} diagrams attached.` : undefined
    }));
  }, [results]);

  const mutation = useMutation({
    mutationFn: async () => {
      if (!dataset) throw new Error("Upload a dataset before generating a report.");
      if (!algorithms.length) throw new Error("Run at least one algorithm first.");
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
          <p className="mt-2 max-w-2xl text-muted-foreground">Aggregate all session algorithm outputs, generate markdown, then export to markdown or browser PDF.</p>
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
              <p className="text-xs uppercase text-muted-foreground">Upload ID</p>
              <p className="mt-1 truncate font-mono text-sm">{dataset?.uploadId ?? "No dataset"}</p>
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

        {dataset && algorithms.length ? <MarkdownReportViewer markdown={markdown} /> : <EmptyState title="Run analysis first" description="Reports are generated by collecting previous algorithm outputs from this browser session." />}
      </div>
    </div>
  );
}
