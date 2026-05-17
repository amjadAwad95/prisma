"use client";

import { motion } from "framer-motion";
import { useRef } from "react";
import { Activity, Database, FileCheck2, Gauge, Sparkles } from "lucide-react";
import { AlgorithmCard } from "@/components/analytics/algorithm-card";
import { FloatingActionButtons } from "@/components/analytics/floating-action-buttons";
import { MetricCard } from "@/components/analytics/metric-card";
import { SessionHistoryPanel } from "@/components/analytics/session-history-panel";
import { UploadDropzone } from "@/components/analytics/upload-dropzone";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAnalyticsStore } from "@/store/session-store";
import { algorithmCatalog, methodLabel } from "@/utils/algorithms";
import { formatBytes } from "@/lib/utils";

export function DashboardClient() {
  const algorithmsRef = useRef<HTMLDivElement>(null);
  const dataset = useAnalyticsStore((state) => state.dataset);
  const resultsBySession = useAnalyticsStore((state) => state.resultsBySession);
  const clearSession = useAnalyticsStore((state) => state.clearSession);
  const allowed = dataset?.methodTypes ?? [];
  const results = dataset ? resultsBySession[dataset.uploadId] ?? {} : {};

  const scrollToAlgorithms = () => {
    algorithmsRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <Badge variant="outline" className="mb-3 gap-2"><Sparkles className="h-3.5 w-3.5" /> Dashboard</Badge>
          <h1 className="text-4xl font-semibold tracking-tight">Data mining workspace</h1>
          <p className="mt-2 max-w-2xl text-muted-foreground">Upload, inspect, run compatible algorithms, and keep outputs scoped to the selected dataset session.</p>
        </div>
        <Button variant="outline" onClick={clearSession}>Clear session</Button>
      </div>

      <UploadDropzone />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard title="Active dataset" value={dataset ? "1" : "0"} delta={dataset ? "Ready" : undefined} icon={Database} />
        <MetricCard title="Compatible algorithms" value={allowed.length} delta={allowed.length ? "Detected" : undefined} icon={Gauge} onClick={scrollToAlgorithms} className="cursor-pointer hover:opacity-80 transition-opacity" />
        <MetricCard title="Completed analyses" value={Object.keys(results).length} delta={Object.keys(results).length ? "Saved" : undefined} icon={Activity} />
        <MetricCard title="Report status" value={Object.keys(results).length ? "Ready" : "Not done"} icon={FileCheck2} />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
        <div className="space-y-6">
          <Card className="bg-card/75 backdrop-blur-xl">
            <CardHeader>
              <CardTitle>Dataset metadata</CardTitle>
            </CardHeader>
            <CardContent>
              {dataset ? (
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="rounded-2xl border border-border bg-background/60 p-4">
                    <p className="text-xs uppercase text-muted-foreground">Filename</p>
                    <p className="mt-1 truncate font-medium">{dataset.filename}</p>
                  </div>
                  <div className="rounded-2xl border border-border bg-background/60 p-4">
                    <p className="text-xs uppercase text-muted-foreground">Upload ID</p>
                    <p className="mt-1 truncate font-mono text-sm">{dataset.uploadId}</p>
                  </div>
                  <div className="rounded-2xl border border-border bg-background/60 p-4">
                    <p className="text-xs uppercase text-muted-foreground">File size</p>
                    <p className="mt-1 font-medium">{formatBytes(dataset.bytes)}</p>
                  </div>
                  <div className="rounded-2xl border border-border bg-background/60 p-4">
                    <p className="text-xs uppercase text-muted-foreground">Upload date</p>
                    <p className="mt-1 font-medium">{new Date(dataset.uploadedAt).toLocaleString()}</p>
                  </div>
                  <div className="md:col-span-2 rounded-2xl border border-border bg-background/60 p-4">
                    <p className="text-xs uppercase text-muted-foreground">Detected methods</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {allowed.length ? allowed.map((method) => <Badge key={method} variant="success">{methodLabel(method)}</Badge>) : <span className="text-sm text-muted-foreground">No compatible methods returned yet.</span>}
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Upload a dataset to populate metadata, file details, detected columns, and compatibility results.</p>
              )}
            </CardContent>
          </Card>

          <div className="grid gap-4 md:grid-cols-2" ref={algorithmsRef}>
            {algorithmCatalog.map((algorithm, index) => {
              const enabled = allowed.includes(algorithm.method);
              return (
                <motion.div key={algorithm.method} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.05 }}>
                  <AlgorithmCard
                    {...algorithm}
                    enabled={enabled}
                    reason={dataset ? "The preprocessing endpoint did not mark this workflow as compatible with the uploaded dataset." : "Upload a dataset to determine compatibility."}
                  />
                </motion.div>
              );
            })}
          </div>

          {/* <div className="grid gap-6 xl:grid-cols-2">
            <Card className="bg-card/75 backdrop-blur-xl">
              <CardHeader>
                <CardTitle>Recent analyses</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">No analytics timeline yet. Run an algorithm to populate recent activity.</p>
              </CardContent>
            </Card>
            <Card className="bg-card/75 backdrop-blur-xl">
              <CardHeader>
                <CardTitle>Dataset preview</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Preview will appear once dataset rows are available.</p>
              </CardContent>
            </Card>
          </div> */}
        </div>
        <SessionHistoryPanel />
      </div>
      <FloatingActionButtons />
    </div>
  );
}
